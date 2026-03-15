import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="openai-stub")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> JSONResponse:
    payload = await request.json()
    tool_name = next(
        (
            tool["function"]["name"]
            for tool in payload["tools"]
            if tool["function"]["name"] == "final_result"
        ),
        payload["tools"][0]["function"]["name"],
    )
    arguments = json.dumps(
        {
            "activity": "RUNNING",
            "bbox": {
                "min_lon": -1.0,
                "min_lat": -1.0,
                "max_lon": 2.0,
                "max_lat": 2.0,
            },
        }
    )
    return JSONResponse(
        {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 0,
            "model": payload.get("model", "stub-model"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_final_result",
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": arguments,
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {
                "prompt_tokens": 1,
                "completion_tokens": 1,
                "total_tokens": 2,
            },
        }
    )
