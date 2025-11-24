"""Gerador de administradores"""

from app.database import SessionLocal
from app.models import Usuario, Papel
from app.main import gerar_hash_senha

def create_admin():
    """Criação de um usuário com papel de administrador no banco de autenticação"""

    db = SessionLocal()

    email = "admin@wgg.com"
    senha = "admin123"

    # Verifica se já existe
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user:
        print(f"O usuário {email} já existe")
        return

    # Cria o Admin
    print(f"Criando admin: {email}")

    novo_admin = Usuario(
        email=email,
        senha_hashed=gerar_hash_senha(senha),
        papel=Papel.ADMIN
    )

    db.add(novo_admin)
    db.commit()

    print("Admin criado")
    db.close()

if __name__ == "__main__":
    create_admin()
