from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.alerts.models import Alert
from app.interventions.models import Intervention, StatutIntervention
from app.interventions.schemas import InterventionCreate, InterventionUpdate


def get_intervention(db: Session, intervention_id: int) -> Optional[Intervention]:
    return db.query(Intervention).filter(Intervention.id == intervention_id).first()


def get_interventions(
    db: Session,
    *,
    technicien_id: Optional[int] = None,
    statut: Optional[StatutIntervention] = None,
    skip: int = 0,
    limit: int = 50,
) -> Sequence[Intervention]:
    query = db.query(Intervention)
    if technicien_id is not None:
        query = query.filter(Intervention.technicien_id == technicien_id)
    if statut is not None:
        query = query.filter(Intervention.statut == statut)
    return query.order_by(Intervention.date_debut.desc()).offset(skip).limit(limit).all()


def create_intervention(db: Session, data: InterventionCreate, technicien_id: int) -> Intervention:
    intervention = Intervention(
        alert_id=data.alert_id,
        technicien_id=technicien_id,
        description=data.description,
        date_debut=datetime.now(timezone.utc),
        statut=StatutIntervention.en_cours,
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


def update_intervention(db: Session, intervention: Intervention, data: InterventionUpdate) -> Intervention:
    updates = data.model_dump(exclude_unset=True)

    # Si on clôture (terminee/annulee) et qu'aucune date_fin n'est fournie, on la fixe automatiquement.
    if updates.get("statut") in (StatutIntervention.terminee, StatutIntervention.annulee):
        updates.setdefault("date_fin", datetime.now(timezone.utc))

    for field, value in updates.items():
        setattr(intervention, field, value)

    db.commit()
    db.refresh(intervention)
    return intervention