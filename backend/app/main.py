import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import uvicorn

from app.db.session import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

from app.api.requisicoes import router as requisicoes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lê as tabelas do 'Base.metadata' e executa o CREATE TABLE IF NOT EXISTS no startup.
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE itens_requisicao ADD COLUMN IF NOT EXISTS frete VARCHAR(150)"))
    logger.info("Startup concluído: conexão com PostgreSQL e tabelas verificadas.")
    yield


app = FastAPI(
    title="ME Genius - Agente de Compras",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requisicoes_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    # Lê a porta dinamicamente da variável de ambiente no Python
    port = int(os.getenv("BACKEND_PORT"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
