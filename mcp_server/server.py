import json
import os
import httpx
from mcp.server.fastmcp import FastMCP

# Configurações lidas do ambiente
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8001"))

# Inicializa o servidor FastMCP
mcp = FastMCP("ferramentas_compras", host=HOST, port=PORT)

# Constantes
BASE_URL = "https://dummyjson.com/products"
TIMEOUT_SECONDS = 10.0


@mcp.tool()
async def buscar_produtos(termo: str) -> str:
    """Retorna uma lista de produtos relacionados ao termo com ID, título, preço e descrição."""
    url = f"{BASE_URL}/search"
    params = {"q": termo}
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(url, params=params) # chamada HTTP GET assincrona
            response.raise_for_status() # lança exceção se o status da resposta não for 2xx
            data = response.json() # converte a resposta JSON em um dicionário Python
            return json.dumps(data) # retorna a resposta como uma string JSON
    except httpx.HTTPError as exc:
        return json.dumps({"erro": f"Falha ao buscar no catálogo: {str(exc)}"}) # tratamento de erro


@mcp.tool()
async def detalhar_produto(id: int) -> str:
    """Retorna detalhes de um produto, incluindo preço, estoque, especificações e marca."""
    url = f"{BASE_URL}/{id}"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return json.dumps(data)
    except httpx.HTTPError as exc:
        return json.dumps({"erro": f"Falha ao detalhar produto: {str(exc)}"})


if __name__ == "__main__":
    # Roda o servidor com transporte SSE (Server-Sent Events) para comunicação via rede
    mcp.run(transport="sse")
