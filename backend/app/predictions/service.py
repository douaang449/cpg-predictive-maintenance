import os
import joblib
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.predictions.schemas import SensoreReadingInput
from app.machines.sensor_models import SensorReading, Prediction


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..","..","ml","data","baseline_rf.joblib")
MODEL_VERSION = "random_forest_v1"
FEATURES_ORDER = ["ambient_temp_k", "motor_temp_k", "shaft_rpm", "load_torque_nm", "operating_minutes"]
_model =None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Modéle introuvable à {MODEL_PATH}.")
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_failure_probabilty(reading: SensoreReadingInput) -> float:
    model = get_model()
    features = [[getattr(reading, f) for f in FEATURES_ORDER]]
    proba = model.predict_proba(features)[0][1]
    return float (proba)

def process_new_reading(db: Session, reading: SensoreReadingInput) -> Prediction:
    now = datetime.now(timezone.utc)

    sensor_reading = SensorReading(
        machine_id=reading.machine_id,
        timestamp=now,
        temperature=reading.motor_temp_k,
        vitesse=reading.shaft_rpm,
        couple=reading.load_torque_nm,
        usure_min=reading.operating_minutes,
    )
    db.add(sensor_reading)
    db.commit()

    probabilite = predict_failure_probabilty(reading)

    prediction = Prediction(
        machine_id=reading.machine_id,
        reading_timestamp=now,
        reading_machine_id=reading.machine_id,
        probabilite=probabilite,
        modele_version=MODEL_VERSION,
        timestamp=now,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction

