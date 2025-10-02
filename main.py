from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rooms: Dict[str, List[WebSocket]] = {}
room_counts: Dict[str, int] = {}

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    if room not in rooms:
        rooms[room] = []
        room_counts[room] = 0
    rooms[room].append(websocket)
    room_counts[room] += 1
    is_initiator = room_counts[room] == 1
    await websocket.send_json({"type": "role", "isInitiator": is_initiator})

    try:
        while True:
            data = await websocket.receive_text()
            for client in rooms[room]:
                if client != websocket:
                    await client.send_text(data)
    except WebSocketDisconnect:
        rooms[room].remove(websocket)
        room_counts[room] -= 1
        if room_counts[room] == 0:
            del rooms[room]
            del room_counts[room]
