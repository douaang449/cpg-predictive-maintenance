from pydantic import BaseModel, Field
from datetime import datetime

class SensorReadingInput(BaseModel):
    machine_id: int
    ambient_temp_k: float = Field(...,description="Température ambiante en Kelvin" )
    motor_temp_k: float = Field(..., description="Température du moteur/process en Kelvin")
    shaft_rpm: float = Field(...,description="Vitesse de rotation en rpm")
    load_torque_nm: float = Field(..., description="Couple en Nm")
    operating_minutes: float = Field(..., description="Minutes d'utilisation cumuléés")

class PredictionOutput(BaseModel):
    machine_id: int
    probabilite: float
    modele_version: str
    timestamp: datetime

    class Config:
        from_attributes = True  