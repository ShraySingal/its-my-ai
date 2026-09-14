"""
IT'S MY AI — WebSocket Router for Live Telemetry & State Sync
Complies with Sections 40 & 41: Persistent low-overhead telemetry channel.
Streams hardware stats and syncs hologram states in real time.
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.system_service import system_service
from backend.app.core.audit import AuditLogger

router = APIRouter(tags=["WebSocket Telemetry"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Persistent bi-directional telemetry connection.
    Periodically pushes hardware stats and receives client control commands.
    """
    await manager.connect(websocket)
    try:
        # Initial telemetry push
        await websocket.send_json({
            "type": "telemetry",
            "data": system_service.get_telemetry()
        })

        while True:
            # Wait for client messages or stream update periodically
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=2.5)
                parsed = json.loads(data)
                msg_type = parsed.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong", "time": parsed.get("time")})
                elif msg_type == "set_hologram_state":
                    await manager.broadcast({
                        "type": "hologram_state",
                        "state": parsed.get("state", "IDLE")
                    })
            except asyncio.TimeoutError:
                # Periodic low-frequency telemetry broadcast
                await websocket.send_json({
                    "type": "telemetry",
                    "data": system_service.get_telemetry()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
