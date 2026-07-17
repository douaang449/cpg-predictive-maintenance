from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.alerts.models import NiveauAlerte, StatutAlert
from app.alerts.threshold_models import Parametre, ScopeType


class AlertThresholdBase(BaseModel):
    scope_type: ScopeType
    scope_id: str = Field(..., description="type_equipement (ex: 'convoyeur') si scope_type=equipement_type, sinon l'id de la machine en str")
    parametre: Parametre
    seuil_surveillance: float
    seuil_maintenance: float
    seuil_critique: float


class AlertThresholdCreate(AlertThresholdBase):
    pass


class AlertThresholdUpdate(BaseModel):
    seuil_surveillance: Optional[float] = None
    seuil_maintenance: Optional[float] = None
    seuil_critique: Optional[float] = None


class AlertThresholdOut(AlertThresholdBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date_modification: Optional[datetime] = None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    prediction_id: Optional[int] = None
    parametre_declencheur: str
    valeur_mesuree: float
    seuil_depasse: float
    niveau: NiveauAlerte
    statut: StatutAlert
    date_creation: Optional[datetime] = None
    date_fermeture: Optional[datetime] = None