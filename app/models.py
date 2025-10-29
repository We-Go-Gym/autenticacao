"""Modelos das tabelas usando SQLAlchemy para o serviço de autenticação."""

# pylint: disable=too-few-public-methods

import enum

from sqlalchemy import Column, Integer, String, Enum
from app.database import Base


class UserRole(enum.Enum):
    """Enumeração para os papéis de usuário da academia."""

    ADMIN = "admin"
    ALUNO = "aluno"


class User(Base):
    """Representa um usuário  no banco de dados."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ALUNO)
