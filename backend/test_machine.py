from app.core.database import SessionLocal
from app.core.models_registry import *
from app.machines.models import Machine

db = SessionLocal()

machines_to_create = [
    ("Convoyeur Test L", "convoyeur", "Metlaoui"),
    ("Concasseur Test M", "concasseur", "Redeyef"),
    ("Unite Lavage Test H", "unite_lavage", "Mdhilla"),
]

for nom, type_eq, site in machines_to_create:
    m = Machine(nom=nom, type_equipement=type_eq, site=site)
    db.add(m)

db.commit()

for m in db.query(Machine).all():
    print(f"id={m.id}  nom={m.nom}  type={m.type_equipement}")

db.close()