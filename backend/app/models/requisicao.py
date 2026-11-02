from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Requisicao(Base):
    """Guarda a requisição de compra criada."""
    __tablename__ = "requisicoes"

    id = Column(Integer, primary_key=True, index=True) # Número da requisição
    valor_total = Column(Numeric(10, 2), nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="CRIADA")
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 1:N com ItemRequisicao, deletando itens quando a requisição é deletada
    itens = relationship("ItemRequisicao", back_populates="requisicao", cascade="all, delete-orphan")


class ItemRequisicao(Base):
    """Guarda os itens escolhidos no catálogo DummyJSON."""
    __tablename__ = "itens_requisicao"

    id = Column(Integer, primary_key=True, index=True)
    requisicao_id = Column(Integer, ForeignKey("requisicoes.id", ondelete="CASCADE"), nullable=False)

    produto_id = Column(Integer, nullable=True) # ID original do produto na DummyJSON
    nome_produto = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=True)
    descricao = Column(Text, nullable=True)
    frete = Column(String(150), nullable=True)
    preco_unitario = Column(Numeric(10, 2), nullable=False)

    quantidade = Column(Integer, nullable=False, default=1)
    subtotal = Column(Numeric(10, 2), nullable=False)

    requisicao = relationship("Requisicao", back_populates="itens")
