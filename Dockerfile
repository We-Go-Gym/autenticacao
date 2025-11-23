# Dockerfile para a autenticação
FROM python:3.11-slim

WORKDIR /code

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY ./app /code/app

# Comando de Inicialização:
CMD sh -c "python -m app.create_admin && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"