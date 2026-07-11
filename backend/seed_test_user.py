"""
Script ponctuel pour créer un premier utilisateur de test.
À exécuter une seule fois, puis peut être supprimé ou gardé comme
utilitaire de développement (à ne jamais utiliser en production).
"""
from app.core.database import SessionLocal
from app.core.models_registry import *
from app.auth.models import Role, User
from app.core.security import hash_password

db = SessionLocal()

# Créer le rôle s'il n'existe pas encore
role = db.query(Role).filter(Role.nom == "chef_projet").first()
if role is None:
    role = Role(nom="chef_projet")
    db.add(role)
    db.commit()
    db.refresh(role)

# Créer l'utilisateur de test
user = User(
    role_id=role.id,
    nom="Test",
    prenom="Douaa",
    email="douaa.test@cpg.tn",
    mot_de_passe_hash=hash_password("motdepasse123"),
    code_CIN="12345678",
    actif=True,
)
db.add(user)
db.commit()

print(f"Utilisateur créé : {user.prenom} {user.nom}, CIN={user.code_CIN}")
db.close()