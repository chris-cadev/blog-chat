from fastapi import APIRouter, Request
from fastapi.responses import Response

from blog_chat.core.logging import log_business_event

router = APIRouter()

MAX_EVENT_LENGTH = 64
MAX_FIELD_COUNT = 8
MAX_FIELD_KEY_LENGTH = 64
MAX_FIELD_VALUE_LENGTH = 200


@router.post("/api/track")
async def track_client_event(request: Request) -> Response:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    event = str(payload.get("event") or "").strip()
    if not event or len(event) > MAX_EVENT_LENGTH:
        return Response(status_code=400)

    fields = {}
    data = payload.get("data")
    if isinstance(data, dict):
        fields = {
            str(key)[:MAX_FIELD_KEY_LENGTH]: str(value)[:MAX_FIELD_VALUE_LENGTH]
            for key, value in list(data.items())[:MAX_FIELD_COUNT]
        }

    log_business_event(
        "client.event",
        f"Client event: {event}",
        client_event=event,
        **fields,
    )
    return Response(status_code=204)
