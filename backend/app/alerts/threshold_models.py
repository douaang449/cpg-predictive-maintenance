from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from app.core.database import Base
from datetime import datetime, timezone
import enum

class ScopeType(str, enum.Enum):
    equipement_type = "equipement_type"
    machine = "machine"

class Parametre(str, enum.Enum):
    probabilite_panne = "probabilite_panne"
    temperature = "temperature"
    vitesse = "vitesse"
    couple = "couple"

class AlertThreshold(Base):
    __tablename__ = "alert_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    scope_type = Column(Enum(ScopeType), nullable=False)
    scope_id = Column(String(50), nullable=False, index=True)
    parametre = Column(Enum(Parametre), nullable=False)
    seuil_surveillance = Column(Float, nullable=False)
    seuil_maintenance = Column(Float, nullable=False)
    seuil_critique = Column(Float, nullable=False)
    date_modification = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))                       