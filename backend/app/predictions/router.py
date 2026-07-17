from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.predictions.schemas import SensoreReadingInput, PredictionOutput
from app.predictions.service import process_new_reading

router= APIRouter(prefix="/predictions", tags=["Prédictions"])

@router.post("", response_model=PredictionOutput)
def create_prediction(
    reading: SensoreReadingInput,
    db: Session = Depends(get_db),
    current_user : User = Depends(get_current_user),
):
    prediction = process_new_reading(db, reading)
    return PredictionOutput(
        machine_id=prediction.machine_id,
        probabilite=prediction.probabilite,
        modele_version=prediction.modele_version,
        timestamp=prediction.timestamp,
    )

