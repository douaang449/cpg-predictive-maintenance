from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base 
import enum
from datetime import datetime, timezone

class StatutOperationnel(str, enum.Enum):
    production ="production"
    arret_planifie = "arret_planifie"
    maintenance ="maintenance"
    hors_service ="hors_service"

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    type_equipement = Column(String(50), nullable=False, index=True)
    site = Column(String(100), nullable=False)
    statut_operationnel = Column(Enum(StatutOperationnel), default=StatutOperationnel.production)
    technicien_id = Column(Integer,ForeignKey("users.id"), nullable=True)
    date_installation = Column(DateTime(timezone=True), nullable=True)

    technicien = relationship("User", back_populates="machines_assignees")
    readings = relationship("SensorReading", back_populates="machine")
    predictions = relationship("Prediction", back_populates="machine")
    alerts = relationship("Alert", back_populates="machine")
