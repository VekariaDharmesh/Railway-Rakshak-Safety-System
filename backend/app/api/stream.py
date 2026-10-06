from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from ..services.realtime_service import realtime_broadcaster
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Realtime Stream"])

@router.get("/stream")
async def sse_event_stream():
    """
    Server-Sent Events (SSE) telemetry and event stream.
    Streams live telemetry, new threats, incident updates, and dispatch orders to Cyber-NOC dashboards.
    """
    async def event_generator():
        queue = realtime_broadcaster.register_sse()
        try:
            # Yield initial connection heartbeat
            yield "event: connected\ndata: {\"status\": \"ONLINE\", \"message\": \"Cyber-NOC telemetry stream active\"}\n\n"
            while True:
                msg = await queue.get()
                yield msg
        except Exception as e:
            logger.error(f"SSE client error: {e}")
        finally:
            realtime_broadcaster.unregister_sse(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for bidirectional operational communication.
    Clients receive real-time telemetry, panic alerts, and incident updates.
    """
    await realtime_broadcaster.connect_ws(websocket)
    try:
        await websocket.send_json({"event": "connected", "data": {"status": "ONLINE"}})
        while True:
            # Listen for client pings or heartbeats
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        realtime_broadcaster.disconnect_ws(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        realtime_broadcaster.disconnect_ws(websocket)
