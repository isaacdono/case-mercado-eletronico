import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.db.session import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Ao importar os modelos aqui, o SQLAlchemy executa as classes
# que herdam de 'Base' e as registra automaticamente no catálogo 'Base.metadata'.
import app.models

from app.api.requisicoes import router as requisicoes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lê as tabelas do 'Base.metadata' e executa o CREATE TABLE no startup do container.
    logger.info("Inicializando banco de dados e garantindo criação das tabelas...")
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ME Genius - Agente de Compras",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(requisicoes_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    # Lê a porta dinamicamente da variável de ambiente no Python
    port = int(os.getenv("BACKEND_PORT"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
