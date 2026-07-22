from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import require_role
from app.dashboard.schemas import GlobalKPIs
from app.dashboard.service import get_global_kpis

router = APIRouter(prefix ="/dashboard", tags =["Dashboard"])

@router.get("/kpis", response_model=GlobalKPIs)
def road_global_kpis(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("chef_projet")),
):
    return get_global_kpis(db)