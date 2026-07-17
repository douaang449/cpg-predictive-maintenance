from fastapi import FastAPI
from app.core.models_registry import *
from app.auth.router import router as auth_router
from app.machines.router import router as machines_router
from app.alerts.router import router as alerts_router
from app.interventions.router import router as interventions_router
from app.predictions.router import router as predictions_router
app = FastAPI( title = "CPG -Système de Maintenance Prédictive",
               description = "API du système de maintenance prédictive pour la Compagnie des Phosphates de Gafsa",
               version = "0.1.0" ,)

app.include_router(auth_router)
app.include_router(machines_router)
app.include_router(alerts_router)
app.include_router(interventions_router)
app.include_router(predictions_router)
@app.get("/")
def root():
    return {"message": "API Maintenance Prédictive CPG - en fonctionnement"}
               