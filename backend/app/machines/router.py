from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User
from app.core.database import get_db
from app.machines import service
from app.machines.models import StatutOperationnel
from app.machines.schemas import (MachineAssignation,MachineCreate,MachineOut,MachineUpdate)

router = APIRouter(prefix="/machines", tags=["Machines"])

def _get_machine_ou_404(db: Session ,machine_id: int) -> object :
    machine = service.get_machine(db, machine_id)
    if machine is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machine introuvable")
    return machine

@router.post("", response_model=MachineOut, status_code=status.HTTP_201_CREATED)
def creer_machine(
    data: MachineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("chef_projet")),

):
    return service.create_machine(db, data)

@router.get("", response_model=List[MachineOut])

def lister_machines(
    statut_operationnel : Optional[StatutOperationnel] = None,
    site : Optional[str] = None,
    skip: int =0,
    limit: int=50,
    db: Session =Depends(get_db),
    current_user: User =Depends(get_current_user),
):
    technicien_id = current_user.id if current_user.role.nom == "technicien" else None

    return service.get_machines(
        db,
        technicien_id=technicien_id,
        statut_operationnel=statut_operationnel,
        site =site,
        skip=skip,
        limit=limit,

    )

@router.get("/{machine_id}", response_model=MachineOut)

def consulter_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user : User =Depends(get_current_user),
):
    machine= _get_machine_ou_404(db, machine_id)

    if current_user.role.nom == "technicien" and machine.technicien_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Machine non assignée")
    return machine

@router.put("/{machine_id}/assigner", response_model=MachineOut)
def assigner_technicien(
    machine_id: int,
    data: MachineAssignation,
    db: Session =Depends(get_db),
    current_user: User = Depends(require_role("chef_projet")),

):
    machine = _get_machine_ou_404(db, machine_id)

    technicien = db.query(User).filter(User.id == data.technicien_id).first()
    if technicien is None or technicien.role.nom != "technicien":
        raise HTTPException(status.HTTP_404_BAD_REQUEST, "Technicien invalide")
    return service.assigner_technicien(db, machine, technicien)

@router.patch("/{machine_id}/archiver", response_model=MachineOut)

def archiver_machine(
    machine_id: int,
    db: Session =Depends(get_db),
    current_user: User = Depends(require_role("chef_projet")),
):
    machine = _get_machine_ou_404(db, machine_id)
    return service.archiver_machine(db, machine)
    
