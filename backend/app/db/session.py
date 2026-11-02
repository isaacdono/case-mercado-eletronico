import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/requisicoes_db"
)

# cria o pool de conexões com o banco de dados
engine = create_engine(DATABASE_URL)

# Gera uma nova sessão do banco para cada requisição HTTP
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base que todos os modelos das tabelas herdam
Base = declarative_base()


def get_db():
    """Dependência para injeção de sessão do banco nas rotas do FastAPI."""
    db = SessionLocal() # Abre a conexão/sessão com o banco
    try:
        yield db # 'yield' entrega a sessão para a rota usar e pausa a função aqui
    finally:
        db.close() # Quando a rota termina de responder, o código retoma aqui e fecha o banco
