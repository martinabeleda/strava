import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from strava.config import settings
from strava.schemas.routes import BoundingBox
from strava.services.route_search import RouteSearchService


@pytest.mark.anyio
async def test_geocode_place_to_bbox_uses_cache_and_rate_limit(monkeypatch):
    response = httpx.Response(
        200,
        json=[
            {
                "boundingbox": ["-33.89", "-33.84", "151.18", "151.24"],
            }
        ],
        request=httpx.Request("GET", settings.NOMINATIM_SEARCH_URL),
    )
    http_client = AsyncMock()
    http_client.get.return_value = response

    service = RouteSearchService(settings, http_client=http_client)
    loop = asyncio.get_running_loop()
    clock = {"now": 100.0}
    sleep_calls: list[float] = []

    async def fake_sleep(duration: float) -> None:
        sleep_calls.append(duration)
        clock["now"] += duration

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(loop, "time", lambda: clock["now"])

    first_bbox = await service.geocode_place_to_bbox("Sydney Australia")
    second_bbox = await service.geocode_place_to_bbox("Sydney Australia")
    clock["now"] += 0.25
    third_bbox = await service.geocode_place_to_bbox("Melbourne Australia")

    expected_bbox = BoundingBox(min_lon=151.18, min_lat=-33.89, max_lon=151.24, max_lat=-33.84)
    assert first_bbox == expected_bbox
    assert second_bbox == expected_bbox
    assert third_bbox == expected_bbox
    assert http_client.get.await_count == 2
    assert sleep_calls == [0.75]

    await service.aclose()
