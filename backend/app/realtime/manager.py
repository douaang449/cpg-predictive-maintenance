from typing import Dict, Optional
from fastapi import WebSocket

class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections: Dict[int, dict] = {}

    async def connect(self, websocket: WebSocket, user_id: int, role_nom: str) -> None:
        await websocket.accept()
        self.active_connections[user_id] = {"websocket": websocket, "role": role_nom}

    def disconnect(self, user_id: int) -> None:
        self.activate_connections.pop(user_id,None ) 
    async def broadcast_alert(self, payload: dict, techincien_id_cible: Optional[int]) -> None:
        for user_id, conn in list(self.active_connections.items()):
            role= conn["role"]
            doit_recevoir = role == "chef_projet" or (role == "technicien" and user_id == techincien_id_cible)
            if doit_recevoir:
                await self._envoyer(conn["websocket"], payload)    

    @staticmethod
    async def _envoyer(websocket: WebSocket,payload: dict) -> None:
        try: 
            await websocket.send_json(payload)
        except Exception:
            pass               
