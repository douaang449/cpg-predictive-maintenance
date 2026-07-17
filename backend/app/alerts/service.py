from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.alerts.models import Alert, NiveauAlerte, StatutAlert
from app.alerts.schemas import AlertThresholdCreate, AlertThresholdUpdate
from app.alerts.threshold_models import AlertThreshold, Parametre, ScopeType
from app.machines.models import Machine



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
    """Le seuil spécifique à la machine prime sur le seuil par défaut du type d'équipement."""
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
    return None  # normal -> pas d'alerte créée




def evaluer_et_creer_alerte(
    db: Session,
    *,
    machine: Machine,
    parametre: Parametre,
    valeur: float,
    prediction_id: Optional[int] = None,
) -> Optional[Alert]:
    """
    À appeler depuis le service de prédiction de Personne A après chaque
    nouvelle mesure/prédiction :

        alerte = evaluer_et_creer_alerte(
            db, machine=machine,
            parametre=Parametre.probabilite_panne,
            valeur=probabilite_predite,
            prediction_id=prediction.id,
        )

    Retourne l'Alert créée, ou None (aucun seuil dépassé / aucun seuil configuré).
    """
    seuil = _resoudre_seuil(db, machine, parametre)
    if seuil is None:
        return None

    niveau = _niveau_pour_valeur(valeur, seuil)
    if niveau is None:
        return None

    seuil_depasse = {
        NiveauAlerte.surveillance: seuil.seuil_surveillance,
        NiveauAlerte.maintenance: seuil.seuil_maintenance,
        NiveauAlerte.critique: seuil.seuil_critique,
    }[niveau]

    alerte = Alert(
        machine_id=machine.id,
        prediction_id=prediction_id,
        parametre_declencheur=parametre.value,
        valeur_mesuree=valeur,
        seuil_depasse=seuil_depasse,
        niveau=niveau,
        statut=StatutAlert.ouverte,
    )
    db.add(alerte)
    db.commit()
    db.refresh(alerte)
    return alerte



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