from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.machines.models import StatutOperationnel


class MachineBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    type_equipement: str = Field(..., min_length=2, max_length=50)
    site: str = Field(..., min_length=2, max_length=100)


class MachineCreate(MachineBase):
    technicien_id: Optional[int] = None
    date_installation: Optional[datetime] = None


class MachineUpdate(BaseModel):
    
    nom: Optional[str] = None
    type_equipement: Optional[str] = None
    site: Optional[str] = None
    statut_operationnel: Optional[StatutOperationnel] = None
    date_installation: Optional[datetime] = None


class MachineAssignation(BaseModel):
    technicien_id: int


class MachineOut(MachineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    statut_operationnel: StatutOperationnel
    technicien_id: Optional[int] = None
    date_installation: Optional[datetime] = None              