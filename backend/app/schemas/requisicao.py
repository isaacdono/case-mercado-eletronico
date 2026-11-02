from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MensagemHistorico(BaseModel):
    """Mensagem anterior da conversa para manter contexto."""

    role: str
    content: str


class PedidoChatInput(BaseModel):
    """Mensagem digitada pela pessoa no chat com histórico da conversa."""

    mensagem: str
    historico: List[MensagemHistorico] = []


class ItemEscolhido(BaseModel):
    """Item selecionado pelo agente no catálogo."""

    produto_id: Optional[int] = None
    nome_produto: str
    preco_unitario: float
    quantidade: int = 1
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    frete: Optional[str] = None


class DecisaoAgente(BaseModel):
    """Resposta estruturada final do agente."""

    mensagem: str
    itens: List[ItemEscolhido] = []


class ItemRequisicaoOut(ItemEscolhido):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subtotal: float


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
