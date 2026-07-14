from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.alerts.models import Alert
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User
from app.core.database import get_db
from app.interventions import service
from app.interventions.models import StatutIntervention
from app.interventions.schemas import InterventionCreate, InterventionOut, InterventionUpdate

router = APIRouter(prefix="/interventions", tags=["Interventions"])


@router.post("", response_model=InterventionOut, status_code=status.HTTP_201_CREATED)
def creer_intervention(
    data: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("technicien")),
):
    alerte = db.query(Alert).filter(Alert.id == data.alert_id).first()
    if alerte is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alerte introuvable")

    # Le technicien ne peut intervenir que sur une alerte de sa propre machine.
    if alerte.machine.technicien_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Alerte hors de ton périmètre")

    return service.create_intervention(db, data, technicien_id=current_user.id)


@router.get("", response_model=List[InterventionOut])
def lister_interventions(
    statut: Optional[StatutIntervention] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # chef_projet -> toutes les interventions ; technicien -> uniquement les siennes.
    technicien_id = current_user.id if current_user.role.nom == "technicien" else None

    return service.get_interventions(
        db, technicien_id=technicien_id, statut=statut, skip=skip, limit=limit
    )


@router.put("/{intervention_id}", response_model=InterventionOut)
def modifier_intervention(
    intervention_id: int,
    data: InterventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    intervention = service.get_intervention(db, intervention_id)
    if intervention is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Intervention introuvable")

    if current_user.role.nom == "technicien" and intervention.technicien_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ce n'est pas ton intervention")

    return service.update_intervention(db, intervention, data)