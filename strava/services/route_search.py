import asyncio
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Awaitable, Callable

import httpx
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from strava.config import Settings, settings
from strava.models.route import Route
from strava.schemas.routes import (
    Activity,
    BoundingBox,
    RouteSearchInterpretation,
    RouteSearchResponse,
)
from strava.schemas.routes import Route as RouteSchema
from strava.utils.geometry import wkt_to_linestring


@dataclass
class RouteSearchDeps:
    geocode_place: Callable[[str], Awaitable[BoundingBox | None]]


def apply_route_filters(
    query: Query,
    *,
    activity: Activity | None = None,
    name: str | None = None,
    bbox: str | None = None,
) -> Query:
    if activity:
        query = query.filter(Route.activity == activity)

    if name:
        query = query.filter(Route.name.ilike(f"%{name}%"))

    if bbox:
        parts = bbox.split(",")
        if len(parts) != 4:
            raise ValueError("bbox must be 4 comma-separated numbers: minLon,minLat,maxLon,maxLat")
        try:
            minx, miny, maxx, maxy = [float(p) for p in parts]
        except ValueError as exc:
            raise ValueError("bbox values must be numeric") from exc

        envelope = (
            f"POLYGON(({minx} {miny},{maxx} {miny},{maxx} {maxy},{minx} {maxy},{minx} {miny}))"
        )
        return query.filter(func.ST_Intersects(Route.route, envelope))

    return query


def fetch_routes(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 50,
    activity: Activity | None = None,
    name: str | None = None,
    bbox: str | None = None,
) -> list[RouteSchema]:
    query = apply_route_filters(
        db.query(Route),
        activity=activity,
        name=name,
        bbox=bbox,
    )
    results = query.offset(offset).limit(limit).all()
    for result in results:
        result.route = wkt_to_linestring(result.route)
    return [RouteSchema.model_validate(result) for result in results]


def build_route_search_agent(model: Any) -> Agent[RouteSearchDeps, RouteSearchInterpretation]:
    agent = Agent[RouteSearchDeps, RouteSearchInterpretation](
        model=model,
        output_type=RouteSearchInterpretation,
        instructions=(
            "You translate conversational route-search requests into structured filters for a routes database. "
            "Use the `resolve_place_to_bbox` tool whenever the user specifies a place or region. "
            "Only set `activity` when the user clearly states one of RUNNING, HIKING, or SKIING. "
            "Only set `name` when the user asks for a route by title or substring. "
            "Leave fields as null when they are not supported by the request."
        ),
    )

    @agent.tool
    async def resolve_place_to_bbox(
        ctx: RunContext[RouteSearchDeps], place_name: str
    ) -> BoundingBox | None:
        """Resolve a place name into a bounding box suitable for spatial route filtering."""

        return await ctx.deps.geocode_place(place_name)

    return agent


class RouteSearchService:
    def __init__(
        self,
        settings: Settings,
        *,
        agent: Agent[RouteSearchDeps, RouteSearchInterpretation] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings
        self._agent = agent
        self._http_client = http_client or httpx.AsyncClient(
            timeout=httpx.Timeout(settings.NOMINATIM_TIMEOUT_SECONDS),
            headers={"User-Agent": f"{settings.PROJECT_NAME}/route-search"},
        )
        self._geocode_lock = asyncio.Lock()
        self._geocode_cache: dict[str, BoundingBox | None] = {}
        self._last_geocode_request_started_at = 0.0

    def _build_default_agent(self) -> Agent[RouteSearchDeps, RouteSearchInterpretation]:
        if not self.settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY must be configured for conversational route search")

        client = AsyncOpenAI(
            api_key=self.settings.OPENAI_API_KEY,
            base_url=self.settings.OPENAI_BASE_URL,
        )
        provider = OpenAIProvider(openai_client=client)
        model = OpenAIChatModel(self.settings.OPENAI_MODEL, provider=provider)
        return build_route_search_agent(model)

    @property
    def agent(self) -> Agent[RouteSearchDeps, RouteSearchInterpretation]:
        if self._agent is None:
            self._agent = self._build_default_agent()
        return self._agent

    async def aclose(self) -> None:
        await self._http_client.aclose()

    async def geocode_place_to_bbox(self, place_name: str) -> BoundingBox | None:
        normalized_place_name = place_name.strip()
        if normalized_place_name in self._geocode_cache:
            return self._geocode_cache[normalized_place_name]

        async with self._geocode_lock:
            if normalized_place_name in self._geocode_cache:
                return self._geocode_cache[normalized_place_name]

            await self._wait_for_geocode_budget()
            bbox = await self._fetch_geocode_bbox(normalized_place_name)
            self._geocode_cache[normalized_place_name] = bbox
            return bbox

    async def _wait_for_geocode_budget(self) -> None:
        # The public Nominatim service allows at most one request per second per application.
        now = asyncio.get_running_loop().time()
        elapsed = now - self._last_geocode_request_started_at
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
            now = asyncio.get_running_loop().time()
        self._last_geocode_request_started_at = now

    async def _fetch_geocode_bbox(self, place_name: str) -> BoundingBox | None:
        try:
            response = await self._http_client.get(
                self.settings.NOMINATIM_SEARCH_URL,
                params={"q": place_name, "format": "jsonv2", "limit": 1},
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            return None

        if not payload:
            return None

        south, north, west, east = [float(value) for value in payload[0]["boundingbox"]]
        return BoundingBox(min_lon=west, min_lat=south, max_lon=east, max_lat=north)

    async def search(self, query_text: str, db: Session, *, limit: int = 50) -> RouteSearchResponse:
        result = await self.agent.run(
            query_text,
            deps=RouteSearchDeps(geocode_place=self.geocode_place_to_bbox),
        )
        filters = result.output
        routes = fetch_routes(
            db,
            limit=limit,
            activity=filters.activity,
            name=filters.name,
            bbox=filters.bbox.to_query_value() if filters.bbox else None,
        )
        return RouteSearchResponse(query=query_text, filters=filters, routes=routes)


@lru_cache
def get_route_search_service() -> RouteSearchService:
    return RouteSearchService(settings)
