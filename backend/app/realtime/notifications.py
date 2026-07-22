from app.alerts.models import Alert
from app.realtime.manager import manager


async def notifier_nouvelle_alerte(alerte: Alert) -> None:
    payload = {
        "type": "nouvelle_alerte",
        "alert_id": alerte.id,
        "machine_id": alerte.machine_id,
        "niveau": alerte.niveau.value,
        "parametre_declencheur": alerte.parametre_declencheur,
        "valeur_mesuree": alerte.valeur_mesuree,
        "date_creation": alerte.date_creation.isoformat() if alerte.date_creation else None,
    }
    await manager.broadcast_alerte(payload, technicien_id_cible=alerte.machine.technicien_id)