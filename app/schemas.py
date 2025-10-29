"""Pydantic Schemas para validação e resposta de dados de autenticação."""

from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):
    """Enumeração para os papéis de usuário."""

    ADMIN = "admin"
    ALUNO = "aluno"


class UserCreate(BaseModel):
    """Schema para criação de usuário (registro)."""

    email: EmailStr
    password: str
    role: UserRole = UserRole.ALUNO  # Por padrão, quem se registra é aluno


class UserResponse(BaseModel):
    """Schema de usuário retornado pela API (sem senha)."""

    id: int
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema para o Token JWT."""

    access_token: str
    token_type: str
