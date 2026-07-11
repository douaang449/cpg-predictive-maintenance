from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.service import authenticate_user, generate_token_for_user

router = APIRouter(prefix="/auth", tags=["Authentification"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.code_CIN,payload.mot_de_passe)

    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Identifiants invalides"
        )
    token = generate_token_for_user(user)
    return TokenResponse(access_token=token, role=user.role.nom,)