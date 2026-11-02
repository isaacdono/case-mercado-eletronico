import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.db.session import Base, engine

# IMPORTANTE: Ao importar os modelos aqui, o SQLAlchemy executa as classes
# que herdam de 'Base' e as registra automaticamente no catálogo 'Base.metadata'.
# Sem esse import, o 'create_all' abaixo não saberia quais tabelas criar no PostgreSQL.
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado automaticamente no startup do container:
    # Lê as tabelas registradas no 'Base.metadata' e executa o CREATE TABLE no PostgreSQL.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ME Genius - Agente de Compras",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    # Lê a porta dinamicamente da variável de ambiente no Python
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
