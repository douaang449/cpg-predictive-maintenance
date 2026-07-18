from sqlalchemy.orm import Session
from app.alerts.threshold_models import AlertThreshold, ScopeType, Parametre
from app.machines.models import Machine

DEFAULT_THRESHOLDS = {
    Parametre.probabilite_panne: {"surveillance" : 0.20, "maintenance": 0.50, "critique":0.75},
    Parametre.temperature: {"surveillance" : 310.0, "maintenance": 315.0, "critique":320.0},
    Parametre.vitesse:  {"surveillance" : 2200.0, "maintenance": 2500.0, "critique":2800.0},
    Parametre.couple:  {"surveillance" : 60.0, "maintenance": 70.0, "critique": 76.0},
}

def resolve_threshold(db: Session, machine: Machine, parametre: Parametre) -> dict:

    machine_threshold = (
        db.query(AlertThreshold).filter(AlertThreshold.scope_type == ScopeType.machine,
                                        AlertThreshold.scope_id == str(machine.id),
                                        AlertThreshold.parametre == parametre,).first()
    )
    if machine_threshold:
        return{
            "surveillance": machine_threshold.seuil_surveillance,
            "maintenance": machine_threshold.seuil_maintenance,
            "critique": machine_threshold.seuil_critique,
        }
    
    type_threshold = (
        db.query(AlertThreshold).filter(
            AlertThreshold.scope_type == ScopeType.equipement_type,
            AlertThreshold.scope_id == machine.type_equipement,
            AlertThreshold.parametre == parametre,
        ).first()
    )
    if type_threshold:
        return {
            "surveillance": type_threshold.seuil_surveillance,
            "maintenance": type_threshold.seuil_maintenance,
            "critique": type_threshold.seuil_critique,

        }
    return DEFAULT_THRESHOLDS[parametre]

def determine_level(value: float, thresholds: dict) -> str:
    if value >= thresholds["critique"]:
        return "critique"
    if value >= thresholds["maintenance"]:
        return "maintenance"
    if value >= thresholds["surveillance"]:
        return "surveillance"
    return "normal"