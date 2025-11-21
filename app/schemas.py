"""Pydantic Schemas para validação e resposta de dados de autenticação."""

from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr


class Papel(str, Enum):
    """Schema para os papeis"""
    ADMIN = "admin"
    ALUNO = "aluno"


class UsuarioCreate(BaseModel):
    """Schema para criação de usuário (registro)"""

    email: EmailStr
    senha: str
    papel: Papel = Papel.ALUNO


class UsuarioResponse(BaseModel):
    """Schema de usuário retornado pela API (sem senha)."""

    id: int
    email: EmailStr
    papel: Papel

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema para o Token JWT."""

    access_token: str
    token_type: str
