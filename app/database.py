"""Configuração do banco de dados e criação de sessão SQLAlchemy para o auth."""

# pylint: disable=invalid-name

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# URL do banco de dados MySQL 
DATABASE_URL = os.getenv(
    "DATABASE_URL_AUTH", "mysql+pymysql://root:password@mysql-db:3306/wgg_auth_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    """session: Session = Depends(get_session)"""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
