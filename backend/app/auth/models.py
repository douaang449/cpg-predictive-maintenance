from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime, timezone
from app.machines.models import Machine

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    nom = Column(String(100), nullable=False ,index=True)
    prenom = Column(String(100),  nullable=False ,index=True)
    email= Column(String(150),  nullable=False, index=True, unique=True)
    mot_de_passe_hash = Column(String(255), nullable=False)
    date_creation = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    code_CIN = Column(String(20), unique=True ,nullable=False, index=True)
    actif = Column(Boolean, default=True)

    role = relationship("Role", back_populates="users")
    machines_assignees = relationship("Machine", back_populates="technicien")

