import asyncio
import json
from unittest.mock import MagicMock, patch
import pytest
import httpx
from hypothesis import given, strategies as st, settings

from server import buscar_produtos, detalhar_produto


@pytest.mark.asyncio
async def test_buscar_produtos_sucesso():
    """Garante busca correta de produtos com retorno formatado em JSON."""
    
    dados_mock = {
        "products": [{"id": 1, "title": "Laptop Pro 15", "price": 1500.0}],
        "total": 1,
    }

    # Simula resposta HTTP 200 da DummyJSON sem bater na internet
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = dados_mock
    mock_response.raise_for_status.return_value = None

    # Substitui temporariamente a chamada HTTP pelo mock durante o teste
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        res = json.loads(await buscar_produtos("laptop"))
        assert res["products"][0]["title"] == "Laptop Pro 15"
        assert res["products"][0]["price"] == 1500.0


@pytest.mark.asyncio
async def test_detalhar_produto_sucesso():
    """Garante detalhamento de um produto existente pelo ID."""

    dados_mock = {
        "id": 1,
        "title": "Laptop Pro 15",
        "price": 1500.0,
        "category": "laptops",
    }

    # Simula payload com dados completos de um único produto
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = dados_mock
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        res = json.loads(await detalhar_produto(1))
        assert res["id"] == 1
        assert res["price"] == 1500.0


# Gera 25 variações automáticas de texto (strings vazias, emojis, símbolos como '@')
@given(termo=st.text())
@settings(max_examples=25)
def test_buscar_produtos_entradas_arbitrarias_hypothesis(termo):
    """Testa resiliência com termos arbitrários (símbolos, vazios e unicode)."""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"products": [], "total": 0}
    mock_response.raise_for_status.return_value = None

    # Verifica se a tool processa qualquer texto sem estourar exceções não tratadas
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        res = json.loads(asyncio.run(buscar_produtos(termo)))
        assert "products" in res or "erro" in res


# Gera números negativos e zero para simular IDs inexistentes
@given(id_invalido=st.integers(max_value=0))
@settings(max_examples=25)
def test_detalhar_produto_ids_invalidos_hypothesis(id_invalido):
    """Testa tratamento de erro para IDs negativos ou zero com resposta 404."""

    # Monta uma exceção HTTPStatusError simulando um erro 404 da API
    req = httpx.Request("GET", f"https://dummyjson.com/products/{id_invalido}")
    err = httpx.HTTPStatusError("404 Not Found", request=req, response=httpx.Response(404, request=req))

    # Garante que a falha é capturada e devolvida em formato amigável no JSON
    with patch("httpx.AsyncClient.get", side_effect=err):
        res = json.loads(asyncio.run(detalhar_produto(id_invalido)))
        assert "erro" in res
