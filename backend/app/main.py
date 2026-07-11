from fastapi import FastAPI
from app.core.models_registry import *
from app.auth.router import router as auth_router

app = FastAPI( title = "CPG -Système de Maintenance Prédictive",
               description = "API du système de maintenance prédictive pour la Compagnie des Phosphates de Gafsa",
               version = "0.1.0" ,)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "API Maintenance Prédictive CPG - en fonctionnement"}
               