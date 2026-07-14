from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.interventions.models import StatutIntervention

class InterventionCreate(BaseModel):
    alert_id: int
    description: Optional[str] = None

class InterventionUpdate(BaseModel):
    description : Optional[str] = None
    statut : Optional[StatutIntervention] = None
    date_fin: Optional[datetime] = None

class  InterventionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    alert_id : int
    technicien_id: int
    description : Optional[str] = None
    date_debut:datetime
    date_fin: Optional[datetime] = None
    statut:  StatutIntervention