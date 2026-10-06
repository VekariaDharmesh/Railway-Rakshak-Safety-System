import asyncio
import json
from typing import List, Dict, Any
from fastapi import WebSocket

class RealtimeBroadcaster:
    def __init__(self):
        self.sse_queues: List[asyncio.Queue] = []
        self.websocket_connections: List[WebSocket] = []

    def register_sse(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.sse_queues.append(q)
        return q

    register_sse_client = register_sse

    def unregister_sse(self, q: asyncio.Queue):
        if q in self.sse_queues:
            self.sse_queues.remove(q)

    unregister_sse_client = unregister_sse

    async def connect_ws(self, websocket: WebSocket):
        await websocket.accept()
        self.websocket_connections.append(websocket)

    register_ws_client = connect_ws

    def disconnect_ws(self, websocket: WebSocket):
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)

    unregister_ws_client = disconnect_ws

    async def broadcast(self, event_type: str, data: Any):
        msg_payload = {"type": event_type, "data": data}
        json_str = json.dumps(msg_payload, default=str)
        sse_formatted = f"event: {event_type}\ndata: {json_str}\n\n"
        
        # Broadcast to SSE queues
        dead_queues = []
        for q in self.sse_queues:
            try:
                await q.put(sse_formatted)
            except Exception:
                dead_queues.append(q)
        for dq in dead_queues:
            self.unregister_sse(dq)

        # Broadcast to WebSockets
        dead_ws = []
        for ws in self.websocket_connections:
            try:
                await ws.send_text(json_str)
            except Exception:
                dead_ws.append(ws)
        for dws in dead_ws:
            self.disconnect_ws(dws)

realtime_broadcaster = RealtimeBroadcaster()
