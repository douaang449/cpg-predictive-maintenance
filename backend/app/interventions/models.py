from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone
import enum

class StatutIntervention(str, enum.Enum):
    en_cours= "en_cours"
    terminee="terminee"
    annulee = "annulee"

class Intervention(Base):
    __tablename__ ="interventions"

    id = Column(Integer,primary_key=True, nullable=False, index=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)
    technicien_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(500), nullable=True)
    date_debut= Column(DateTime(timezone=True), nullable=False)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    statut = Column(Enum(StatutIntervention), default=StatutIntervention.en_cours)

    alert = relationship("Alert", back_populates="interventions")
    teechnicien = relationship("User")