"""Modelos das tabelas usando SQLAlchemy para o serviço de autenticação."""

# pylint: disable=too-few-public-methods

import enum

from sqlalchemy import Column, Integer, String, Enum
from app.database import Base


class Papel(enum.Enum):
    """Enumeração para os papéis de usuário."""

    ADMIN = "admin"
    ALUNO = "aluno"


class Usuario(Base):
    """Representa um usuário no banco de dados."""

    __tablename__ = "USUARIO"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hashed = Column(String(255), nullable=False)
    papel = Column(Enum(Papel), nullable=False, default=Papel.ALUNO)
