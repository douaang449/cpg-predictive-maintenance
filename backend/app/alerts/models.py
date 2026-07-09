from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone

import enum

class NiveauAlerte(str, enum.Enum):
    normal ="normal" 
    surveillance = "surveillance"
    maintenance ="maintenance"
    critique = "critique"

class StatutAlert(str, enum.Enum):
    ouverte = "ouverte"
    fermee = "fermee"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    parametre_declencheur = Column(String(50), nullable=False)
    valeur_mesuree = Column(Float, nullable=False)
    seuil_depasse = Column(Float, nullable=False)
    niveau = Column(Enum(NiveauAlerte), nullable=False)
    statut= Column(Enum(StatutAlert), default=StatutAlert.ouverte)
    date_creation = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    date_fermeture = Column(DateTime(timezone=True), nullable=True)  

    machine = relationship("Machine", back_populates="alerts")
    interventions = relationship("Intervention", back_populates="alert")   