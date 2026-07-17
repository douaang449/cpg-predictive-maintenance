from app.core.database import SessionLocal
from app.core.models_registry import *
from app.machines.models import Machine

db = SessionLocal()
machine = Machine(nom="Concasseur Test", type_equipement="concasseur", site="Metlaoui")
db.add(machine)
db.commit()
db.refresh(machine)
print(f"Machine créée : id={machine.id}")
db.close()