from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.auth.models import User
from app.core.database import get_db
from app.core.security import decode_access_token
from app.realtime.manager import manager

router = APIRouter(tags=["Temps réel"])

@router.websocket("/ws/dashboard")
async def ws_dashboard(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session =Depends(get_db),
    ):
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=1008)
        return
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id).first() if user_id else None)
    if user is None or not user.actif:
        await websocket.close(code=1008)
        return
    await manager.connect(websocket, user.id, user.role.nom)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user.id)        
