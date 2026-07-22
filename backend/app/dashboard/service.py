from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.machines.models import Machine
from app.alerts.models import Alert, NiveauAlerte, StatutAlert
from app.interventions.models import Intervention, StatutIntervention

def get_total_machines(db: Session) -> int :
    return db.query(func.count(Machine.id)).scalar()

def get_machines_by_alert_level(db:Session) -> dict:
    total = get_total_machines(db)
    open_alert_counts = (db.query(Alert.niveau, func.count(Alert.id)).filter(Alert.statut == StatutAlert.ouverte).group_by(Alert.niveau).all())
    counts ={niveau.value: count for niveau, count in open_alert_counts}

    surveillance =  counts.get("surveillance", 0)
    maintenance =  counts.get("maintenance", 0)
    critique = counts.get("critique", 0)
    machines_with_alert = surveillance +  maintenance + critique
    normal =  total- machines_with_alert

    return {
        "normal": max(normal, 0),
        "surveillance": surveillance,
        "maintenance": maintenance,
        "critique": critique,
    }
def get_active_alerts_breakdown(db: Session) -> dict :
    results = (db.query(Alert.niveau, func.count(Alert.id)).filter(Alert.statut == StatutAlert.ouverte).group_by(Alert.niveau).all())
    counts = {niveau.value: count for niveau, count in results}
    return {
        "normal": 0,
        "surveillance": counts.get("surveillance",0),
        "maintenance": counts.get("maintenance",0),
        "critique": counts.get("critique",0),
    }

def get_active_alerts_count(db: Session) -> int:
    return(db.query(func.count(Alert.id)).filter(Alert.statut == StatutAlert.ouverte).scalar())

def get_mttr_hours(db: Session) -> float | None:
    result = (db.query(func.avg(func.extract("epoch", Alert.date_fermeture -Alert.date_creation)))
              .join(Intervention, Intervention.alert_id == Alert.id).filter(
                  Alert.statut == StatutAlert.fermee,
                  Alert.date_fermeture.isnot(None),
                  Intervention.statut == StatutIntervention.terminee,
              ).scalar())
    if result is None:
        return None
            
    return round(result / 3600, 2)

def get_availability_rate(db: Session) -> float :
    total = get_total_machines(db)
    if total == 0:
        return 100.0
    degraded_count = (db.query(func.count(func.distinct(Alert.machine_id))).filter(Alert.statut == StatutAlert.ouverte,Alert.niveau.in_([NiveauAlerte.maintenance, NiveauAlerte.critique]),).scalar())
    available = total - degraded_count
    return round((available/total)*100, 1)

def get_global_kpis(db: Session) -> dict :
    return{
        "total_machines": get_total_machines(db),
        "machines_by_alert_level": get_machines_by_alert_level(db),
        "active_alerts_count": get_active_alerts_count(db),
        "alerts_by_level": get_active_alerts_breakdown(db),
        "mttr_hours": get_mttr_hours(db),
        "availability_rate": get_availability_rate(db),
    }