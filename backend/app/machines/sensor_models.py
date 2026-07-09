from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    machine_id = Column(Integer,  ForeignKey("machines.id"), primary_key=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True, default=lambda: datetime.now(timezone.utc))
    temperature = Column(Float, nullable=False)
    vitesse =Column(Float, nullable=False)
    couple = Column(Float, nullable=False)
    usure_min = Column(Float, nullable=False)

    machine = relationship("Machine", back_populates="readings")
    

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    reading_timestamp = Column(DateTime(timezone=True), nullable=False)
    reading_machine_id =Column(Integer, nullable=False)
    probabilite = Column(Float, nullable=False)
    modele_version = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    machine = relationship("Machine", back_populates="predictions")    