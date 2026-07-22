from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.alerts.models import Alert, NiveauAlerte, StatutAlert
from app.alerts.schemas import AlertThresholdCreate, AlertThresholdUpdate
from app.alerts.threshold_models import AlertThreshold, Parametre, ScopeType
from app.machines.models import Machine
from app.predictions.schemas import SensorReadingInput
from app.alerts.threshold_service import resolve_threshold, determine_level

def create_threshold(db: Session, data: AlertThresholdCreate) -> AlertThreshold:
    seuil = AlertThreshold(**data.model_dump())
    db.add(seuil)
    db.commit()
    db.refresh(seuil)
    return seuil


def get_thresholds(
    db: Session,
    *,
    scope_type: Optional[ScopeType] = None,
    parametre: Optional[Parametre] = None,
) -> Sequence[AlertThreshold]:
    query = db.query(AlertThreshold)
    if scope_type is not None:
        query = query.filter(AlertThreshold.scope_type == scope_type)
    if parametre is not None:
        query = query.filter(AlertThreshold.parametre == parametre)
    return query.all()


def update_threshold(db: Session, seuil: AlertThreshold, data: AlertThresholdUpdate) -> AlertThreshold:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(seuil, field, value)
    db.commit()
    db.refresh(seuil)
    return seuil


def _resoudre_seuil(db: Session, machine: Machine, parametre: Parametre) -> Optional[AlertThreshold]:

    seuil_machine = (
        db.query(AlertThreshold)
        .filter(
            AlertThreshold.parametre == parametre,
            AlertThreshold.scope_type == ScopeType.machine,
            AlertThreshold.scope_id == str(machine.id),
        )
        .first()
    )
    if seuil_machine is not None:
        return seuil_machine

    return (
        db.query(AlertThreshold)
        .filter(
            AlertThreshold.parametre == parametre,
            AlertThreshold.scope_type == ScopeType.equipement_type,
            AlertThreshold.scope_id == machine.type_equipement,
        )
        .first()
    )


def _niveau_pour_valeur(valeur: float, seuil: AlertThreshold) -> Optional[NiveauAlerte]:
    if valeur >= seuil.seuil_critique:
        return NiveauAlerte.critique
    if valeur >= seuil.seuil_maintenance:
        return NiveauAlerte.maintenance
    if valeur >= seuil.seuil_surveillance:
        return NiveauAlerte.surveillance
    return None  




def evaluate_and_create_alert(
    db: Session,
    machine: Machine,
    reading: SensorReadingInput,
    probabilite: float,
    prediction_id: int,
) -> Alert | None:
    checks = [
        (Parametre.probabilite_panne, probabilite),
        (Parametre.temperature, reading.motor_temp_k),
        (Parametre.vitesse, reading.shaft_rpm),
        (Parametre.couple, reading.load_torque_nm),
    ]

    worst_level = "normal"
    worst_param = None
    worst_value = None
    worst_threshold = None

    
    for parametre, value in checks:
        thresholds = resolve_threshold(db, machine, parametre)
        level = determine_level(value, thresholds)
        
      
        
        if LEVEL_ORDER[level] > LEVEL_ORDER[worst_level]:
            worst_level = level
            worst_param = parametre
            worst_value = value
            worst_threshold = thresholds[level] if level != "normal" else None
          
   

    if worst_level == "normal":
        return None

    existing = (
        db.query(Alert)
        .filter(Alert.machine_id == machine.id, Alert.statut == StatutAlert.ouverte)
        .first()
    )
    if existing:
        existing.valeur_mesuree = worst_value
        existing.niveau = LEVEL_MAP[worst_level]
        existing.parametre_declencheur = worst_param.value
        existing.seuil_depasse = worst_threshold
        existing.prediction_id = prediction_id if worst_param == Parametre.probabilite_panne else None
        db.commit()
        db.refresh(existing)
        return existing

    alert = Alert(
        machine_id=machine.id,
        prediction_id=prediction_id if worst_param == Parametre.probabilite_panne else None,
        parametre_declencheur=worst_param.value,
        valeur_mesuree=worst_value,
        seuil_depasse=worst_threshold,
        niveau=LEVEL_MAP[worst_level],
        statut=StatutAlert.ouverte,
        date_creation=datetime.now(timezone.utc),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert



def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.id == alert_id).first()


def get_alerts(
    db: Session,
    *,
    machine_id: Optional[int] = None,
    technicien_id: Optional[int] = None,
    statut: Optional[StatutAlert] = None,
    niveau: Optional[NiveauAlerte] = None,
    skip: int = 0,
    limit: int = 50,
) -> Sequence[Alert]:
    query = db.query(Alert)
    if machine_id is not None:
        query = query.filter(Alert.machine_id == machine_id)
    if technicien_id is not None:
        query = query.join(Machine, Machine.id == Alert.machine_id).filter(
            Machine.technicien_id == technicien_id
        )
    if statut is not None:
        query = query.filter(Alert.statut == statut)
    if niveau is not None:
        query = query.filter(Alert.niveau == niveau)
    return query.order_by(Alert.date_creation.desc()).offset(skip).limit(limit).all()


def fermer_alerte(db: Session, alerte: Alert) -> Alert:
    alerte.statut = StatutAlert.fermee
    alerte.date_fermeture = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alerte)
    return alerte

LEVEL_ORDER = {"normal": 0 , "surveillance": 1 , "maintenance": 2 , "critique": 3}
LEVEL_MAP = {
    "surveillance": NiveauAlerte.surveillance,
    "maintenance": NiveauAlerte.maintenance,
    "critique": NiveauAlerte.critique,
}

def evaluate_and_create_alert(
        db: Session,
        machine: Machine,
        reading: SensorReadingInput,
        probabilite: float,
        prediction_id: int,

) -> Alert | None :
    checks = [(Parametre.probabilite_panne, probabilite),
              (Parametre.temperature, reading.motor_temp_k),
              (Parametre.vitesse, reading.shaft_rpm),
              (Parametre.couple, reading.load_torque_nm)]
    worst_level = "normal"
    worst_param = None
    worst_value = None
    worst_threshold = None

    for parametre, value in checks:
        thresholds = resolve_threshold(db, machine,parametre)
        level = determine_level(value, thresholds)
       
        if LEVEL_ORDER[level] > LEVEL_ORDER[worst_level]:
            worst_level = level
            worst_param = parametre
            worst_value =value
            worst_threshold =thresholds[level]
           
    if worst_level == "normal":
        return None

    existing = (db.query(Alert).filter(Alert.machine_id == machine.id, Alert.statut == StatutAlert.ouverte).first()) 
    if existing:
            existing.valeur_mesuree = worst_value
            existing.niveau = LEVEL_MAP[worst_level]
            existing.parametre_declencheur = worst_param.value
            existing.seuil_depasse = worst_threshold
            db.commit()
            db.refresh(existing)
            return existing

    alert =Alert(machine_id=machine.id,
                     prediction_id=prediction_id if worst_param == Parametre.probabilite_panne else None,
                     parametre_declencheur= worst_param.value,
                     valeur_mesuree=worst_value,
                     seuil_depasse=worst_threshold,
                     niveau=LEVEL_MAP[worst_level],
                     statut=StatutAlert.ouverte,
                     date_creation=datetime.now(timezone.utc),)  
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert 