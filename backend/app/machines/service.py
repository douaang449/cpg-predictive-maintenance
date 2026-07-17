from typing import Optional, Sequence

from sqlalchemy.orm import Session, joinedload

from app.auth.models import User
from app.machines.models import Machine, StatutOperationnel
from app.machines.schemas import MachineCreate, MachineUpdate

def get_machine(db:Session, machine_id:int) -> Optional[Machine]:
    return(
        db.query(Machine)
        .options(joinedload(Machine.technicien))
        .filter(Machine.id == machine_id)
        .first()
    )

def get_machines(
        db: Session,
        *,
        technicien_id : Optional[int]= None,
        statut_operationnel : Optional[StatutOperationnel] = None,
        site : Optional[str] = None,
        skip : int = 0,
        limit: int =50 ,
) -> Sequence [Machine]:
    query = db.query(Machine).options(joinedload(Machine.technicien)) 

    if technicien_id is not None :
        query = query.filter(Machine.technicien_id == technicien_id)
    if statut_operationnel is not None :
        query = query.filter(Machine.statut_operationnel == statut_operationnel)
    if site is not None:
        query = query.filter(Machine.site == site) 
    return query.offset(skip).limit(limit).all()

def create_machine(db: Session, data: MachineCreate) ->Machine:
    machine =Machine(
        nom=data.nom,
        type_equipement=data.type_equipement,
        site=data.site,
        technicien_id=data.technicien_id,
        date_installation=data.date_installation,
        statut_operationnel=StatutOperationnel.production,

    )
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine 

def update_machine(db: Session, machine: Machine, data: MachineUpdate) -> Machine :
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(machine, field, value)
    db.commit()
    db.refresh(machine)
    return machine     

def archiver_machine(db : Session ,machine : Machine) -> Machine:

    machine.statut_operationnel =StatutOperationnel.hors_service
    db.commit()
    db.refresh(machine)
    return machine         