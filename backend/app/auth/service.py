from sqlalchemy.orm import Session, joinedload
from app.auth.models import User
from app.core.security import verify_password, create_access_token

def authenticate_user(db: Session, code_CIN:str, mot_de_passe:str) -> User | None:
    user = (db.query(User).options(joinedload(User.role)).filter(User.code_CIN == code_CIN).first())

    if user is None :
        return None
    if not user.actif:
        return None
    if not verify_password(mot_de_passe, user.mot_de_passe_hash):
        return None
    return user

def generate_token_for_user(user: User) -> str:
    return create_access_token({
        "sub": str(user.id),
        "role": user.role.nom,
    })