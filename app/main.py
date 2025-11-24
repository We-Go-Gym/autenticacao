"""Módulo de inicialização da aplicação de Autenticação"""
# pylint: disable=raise-missing-from, no-member

import os
import time
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from passlib.context import CryptContext
import jwt

from app.database import Base, engine, get_session
from app import models, schemas


MAX_RETRIES = 10
RETRY_DELAY = 3
for i in range(MAX_RETRIES):
    try:
        Base.metadata.create_all(engine)
        print("INFO: Tabelas criadas com sucesso no banco de dados")
        break
    except OperationalError:
        if i < MAX_RETRIES - 1:
            print(f"Aguardando banco de dados... ({i+1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
        else:
            raise

app = FastAPI(title="Serviço de Autenticação WGG")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "supersecret_dev_key_wgg")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Funções auxiliares


def gerar_hash_senha(senha: str) -> str:
    """Cria o código hash da senha"""
    return pwd_context.hash(senha)


def verificar_senha(senha_plana: str, senha_hashed: str) -> bool:
    """Verifica se a senha é válida"""
    return pwd_context.verify(senha_plana, senha_hashed)


def criar_token_acesso(dados: dict):
    """Gera o token JWT de acesso"""
    a_codificar = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    a_codificar.update({"exp": expiracao})
    return jwt.encode(a_codificar, SECRET_KEY, algorithm=ALGORITHM)


def obter_usuario_atual(token: str = Depends(oauth2_scheme)):
    """Verifica o token do usuário"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


# Rotas


@app.post("/register", response_model=schemas.UsuarioResponse, status_code=201)
def registrar_usuario(
    usuario: schemas.UsuarioCreate, session: Session = Depends(get_session)
):
    """Registra um novo usuário."""
    usuario_existente = (
        session.query(models.Usuario)
        .filter(models.Usuario.email == usuario.email)
        .first()
    )
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hashed = gerar_hash_senha(usuario.senha)

    novo_usuario = models.Usuario(
        email=usuario.email, senha_hashed=senha_hashed, papel=usuario.papel
    )
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    return novo_usuario


@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # O Swagger manda os dados aqui
    session: Session = Depends(get_session),
):
    """Autentica o usuário e retorna o Token JWT"""

    # O Swagger envia 'username' mas nós usamos isso como email
    email_recebido = form_data.username
    senha_recebida = form_data.password

    usuario = (
        session.query(models.Usuario)
        .filter(models.Usuario.email == email_recebido)
        .first()
    )

    if not usuario or not verificar_senha(senha_recebida, usuario.senha_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_dados = {"sub": usuario.email, "role": usuario.papel.value, "id": usuario.id}
    token = criar_token_acesso(token_dados)

    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UsuarioResponse)
def ler_usuario_atual(
    email_usuario: str = Depends(obter_usuario_atual),
    session: Session = Depends(get_session),
):
    """Rota protegida: Retorna os dados do usuário logado."""
    usuario = (
        session.query(models.Usuario)
        .filter(models.Usuario.email == email_usuario)
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@app.get("/health")
def health_check():
    """Rota para ver a saúde do sistema"""
    return {"status": "ok"}
