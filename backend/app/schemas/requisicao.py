from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PedidoChatInput(BaseModel):
    """Mensagem digitada pela pessoa no chat."""

    mensagem: str


class ItemRequisicaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: Optional[int] = None
    nome_produto: str
    preco_unitario: float
    quantidade: int
    subtotal: float
    categoria: Optional[str] = None
    descricao: Optional[str] = None


class RequisicaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int 
    valor_total: float
    status: str
    criado_em: datetime
    itens: List[ItemRequisicaoOut] = []


class RespostaAgente(BaseModel):
    """Resposta exibida no chat."""

    sucesso: bool
    mensagem: str
    requisicao: Optional[RequisicaoOut] = None
