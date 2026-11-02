import logging
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.requisicao import Requisicao, ItemRequisicao
from app.schemas.requisicao import PedidoChatInput, RequisicaoOut, RespostaAgente
from app.agent.runner import executar_agente

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/requisicoes", tags=["Requisicoes"])


@router.get("", response_model=List[RequisicaoOut])
def listar_requisicoes(db: Session = Depends(get_db)):
    """Retorna todas as requisições salvas no PostgreSQL com seus itens."""
    
    # joinedload faz um único SELECT com JOIN nos itens (evita o problema de N+1 queries)
    return (
        db.query(Requisicao)
        .options(joinedload(Requisicao.itens))
        .order_by(Requisicao.criado_em.desc())
        .all()
    )


@router.post("", response_model=RespostaAgente)
async def processar_pedido_chat(
    pedido: PedidoChatInput,
    db: Session = Depends(get_db)  # Injeta a sessão do banco criada pelo get_db()
):
    """Aciona o agente autônomo e registra a requisição caso aprovada."""

    try:
        decisao = await executar_agente(pedido.mensagem)

        if not decisao.itens:
            logger.info("Nenhuma requisição gerada para o pedido.")
            return RespostaAgente(
                sucesso=False,
                mensagem=decisao.mensagem,
                requisicao=None
            )

        total = sum(it.preco_unitario * it.quantidade for it in decisao.itens)

        # Ao passar a lista em `itens=...`, o relationship do SQLAlchemy preenche o requisicao_id sozinho
        nova_requisicao = Requisicao(
            valor_total=total,
            status="CRIADA",
            itens=[
                ItemRequisicao(
                    **it.model_dump(),  # Desempacota o Pydantic em dict para o model do SQLAlchemy
                    subtotal=it.preco_unitario * it.quantidade,
                )
                for it in decisao.itens
            ],
        )
        db.add(nova_requisicao)
        db.commit()
        db.refresh(nova_requisicao)  # Recarrega do banco o id e criado_em gerados no INSERT
        logger.info("Requisição #%d salva no banco com valor total %.2f", nova_requisicao.id, total)

        return RespostaAgente(
            sucesso=True,
            mensagem=decisao.mensagem,
            requisicao=nova_requisicao
        )

    except Exception as exc:
        db.rollback()  # Desfaz qualquer operação pendente na transação em caso de erro
        logger.error("Erro ao processar requisição: %s", exc, exc_info=True)
        return RespostaAgente(
            sucesso=False,
            mensagem="Desculpe, ocorreu uma instabilidade momentânea ao processar sua requisição. Por favor, tente novamente.",
            requisicao=None
        )
