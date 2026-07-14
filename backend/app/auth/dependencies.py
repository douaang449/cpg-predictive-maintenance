from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db

from app.core.security import decode_access_token
from app.auth.models import User

bearer_scheme = HTTPBearer()
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session =Depends(get_db),
) -> User :
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = (db.query(User).options(joinedload(User.role))
                          .filter(User.id == int(user_id)).first()
     )
    
    if user is None or not user.actif:
        raise credentials_exception
    return user

def require_role(*roles_autorises: str):

    def role_cheker(current_user: User =Depends(get_current_user)) -> User :
        if current_user.role.nom not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé : rôle insuffisant",
            )
        return current_user
    return role_cheker