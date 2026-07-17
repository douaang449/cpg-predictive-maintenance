from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.alerts import service
from app.alerts.models import NiveauAlerte, StatutAlert
from app.alerts.schemas import(
    AlertOut,
    AlertThresholdCreate,
    AlertThresholdOut,
    AlertThresholdUpdate
)

from app.alerts.threshold_models import Parametre, ScopeType
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User
from app.core.database import get_db

router = APIRouter(tags=["Alertes"])

@router.post("/alert-thresholds", response_model=AlertThresholdOut, status_code=status.HTTP_201_CREATED)
def creer_seuil(
    data: AlertThresholdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef_projet")),

):
    return service.create_threshold(db, data)

@router.get("/alert-thresholds", response_model=List[AlertThresholdOut])
def lister_seuils(
    scope_type: Optional[ScopeType] = None,
    parametre: Optional[Parametre] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef_projet")),
):
    return service.get_thresholds(db, scope_type=scope_type, parametre=parametre)


@router.put("/alert-thresholds/{seuil_id}", response_model=AlertThresholdOut)
def modifier_seuil(
    seuil_id: int,
    data: AlertThresholdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef_projet")),
):
    seuil = db.query(service.AlertThreshold).filter(service.AlertThreshold.id == seuil_id).first()
    if seuil is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Seuil introuvable")
    return service.update_threshold(db, seuil, data)




@router.get("/alerts", response_model=List[AlertOut])
def lister_alertes(
    machine_id: Optional[int] = None,
    statut: Optional[StatutAlert] = None,
    niveau: Optional[NiveauAlerte] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
   
    technicien_id = current_user.id if current_user.role.nom == "technicien" else None

    return service.get_alerts(
        db,
        machine_id=machine_id,
        technicien_id=technicien_id,
        statut=statut,
        niveau=niveau,
        skip=skip,
        limit=limit,
    )


@router.patch("/alerts/{alert_id}/fermer", response_model=AlertOut)
def fermer_alerte(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alerte = service.get_alert(db, alert_id)
    if alerte is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alerte introuvable")

    if current_user.role.nom == "technicien" and alerte.machine.technicien_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Alerte hors de ton périmètre")

    return service.fermer_alerte(db, alerte)