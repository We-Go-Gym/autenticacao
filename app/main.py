"""Módulo de inicialização da aplicação"""

import os
import time
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import jwt

from app.database import Base, engine, get_session
from app import models, schemas


MAX_RETRIES = 10
RETRY_DELAY = 3

for i in range(MAX_RETRIES):
    try:
        # Tenta criar as tabelas onde a conexão é feita e falha
        Base.metadata.create_all(engine)
        print("INFO: Tabelas criadas com sucesso no banco de dados")
        break

    except OperationalError as e:
        if i < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
        else:
            raise

app = FastAPI(title="Serviço de autenticação WGG")

# Configuração de Segurança
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "supersecret_dev_key_wgg")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Contexto de Hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Funções de Segurança (Hashing e JWT)


def hash_password(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha plana corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Cria um novo token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Schemas locais para este endpoint


class LoginRequest(BaseModel):
    """Schema para o corpo da requisição de login."""

    email: EmailStr
    password: str


# Endpoints da API


@app.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    """Endpoint para registrar um novo usuário (ALUNO ou ADMIN)."""
    existing_user = (
        session.query(models.User).filter(models.User.email == user.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_pw = hash_password(user.password)

    # Criando o novo usuário no banco
    user_db = models.User(
        email=user.email,
        password_hash=hashed_pw,
        role=user.role,  # O 'role' vem do schema UserCreate
    )

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    # Retorna o usuário criado sem a senha
    return user_db


@app.post("/login", response_model=schemas.Token)
def login_user(request: LoginRequest, session: Session = Depends(get_session)):
    """Endpoint para autenticar um usuário e retornar um token JWT."""
    user_db = (
        session.query(models.User).filter(models.User.email == request.email).first()
    )

    # Verifica se o usuário existe e se a senha está correta
    if not user_db or not verify_password(request.password, user_db.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": user_db.email,
        "role": user_db.role.value,  #  admin or aluno
    }
    token = create_access_token(data=token_data)

    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Endpoint para buscar um usuário pelo ID (útil para admins)."""
    user_db = session.query(models.User).get(user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db


@app.get("/health")
def health_check():
    """Endpoint de verificação de saúde do serviço."""
    return {"status": "ok"}
