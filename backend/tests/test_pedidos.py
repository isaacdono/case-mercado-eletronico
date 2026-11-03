import json
import os
import urllib.request
import pytest

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    f"http://localhost:{os.getenv('BACKEND_PORT', '8000')}/requisicoes",
)

CASOS_DE_TESTE = [
    pytest.param(
        "Compre 3 laptops de até US$ 2.000 cada",
        True,
        2000.0,
        id="1_compra_3_laptops_ate_2000",
    ),
    pytest.param(
        "Compre 2 smartphones Samsung de até US$ 1.000 cada",
        True,
        1000.0,
        id="2_compra_2_samsung_ate_1000",
    ),
    pytest.param(
        "Compre 1 laptop que custe no máximo US$ 300",
        False,
        None,
        id="3_orcamento_insuficiente_laptop_300",
    ),
    pytest.param(
        "Compre 1 tablet de até US$ 800",
        True,
        800.0,
        id="4_compra_1_tablet_ate_800",
    ),
    pytest.param(
        "Quanto é 2 + 2?",
        False,
        None,
        id="5_guardrail_fora_de_escopo",
    ),
]


@pytest.mark.parametrize("mensagem,espera_requisicao,teto_unitario", CASOS_DE_TESTE)
def test_pedidos_agente(mensagem: str, espera_requisicao: bool, teto_unitario: float | None):
    """Testa cada um dos 5 pedidos contra o endpoint /requisicoes validando a decisão do agente."""
    
    payload = json.dumps({"mensagem": mensagem, "historico": []}).encode("utf-8")
    req = urllib.request.Request(
        BACKEND_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        assert resp.status == 200
        dados = json.loads(resp.read().decode("utf-8"))

    criou_req = bool(dados.get("sucesso") and dados.get("requisicao"))
    assert criou_req is espera_requisicao

    if criou_req and teto_unitario is not None:
        itens = dados["requisicao"].get("itens", [])
        assert len(itens) > 0
        assert all(i["preco_unitario"] <= teto_unitario for i in itens)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
