from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.auth.schemas import LoginRequest, TokenResponse, UserOut
from app.auth.service import authenticate_user, generate_token_for_user
from app.auth.models import User


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




@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        nom=current_user.nom,
        prenom=current_user.prenom,
        code_CIN=current_user.code_CIN,
        email=current_user.email,
        role=current_user.role.nom,
        actif=current_user.actif,
    )


@router.get("/admin-only")
def admin_only_route(current_user: User = Depends(require_role("chef_projet"))):
    return {"message": f"Bienvenue {current_user.prenom}, tu es bien chef_projet"}