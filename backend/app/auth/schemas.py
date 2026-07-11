from pydantic import BaseModel, Field
import re

class LoginRequest(BaseModel):
    code_CIN: str = Field(...,min_lenght=8,max_length=8, pattern=r"^\d{8}$", description="Code CIN de l'utilisateur")
    mot_de_passe: str =Field(...,min_lenght=1)

  

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserOut(BaseModel):
    id: int
    nom: str
    prenom: str
    code_CIN: str
    email: str
    role: str
    actif: bool

    class Config:
        from_attributes = True