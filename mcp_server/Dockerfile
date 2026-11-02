FROM python:3.12-slim 

WORKDIR /app

# Instala o gerenciador de dependências uv-astral
RUN pip install uv

# Aproveita cache copiando apenas dependências primeiro
COPY requirements.txt .

# Instala as dependências no Python global do container
RUN uv pip install --system --no-cache -r requirements.txt

# Copia o código da aplicação
COPY . .

ENV MCP_PORT=8001
EXPOSE ${MCP_PORT}

CMD ["python", "server.py"]
