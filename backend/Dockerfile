FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copia o código da aplicação dps de instalar as deps para aproveitar o cache
COPY . . 

CMD ["python", "-m", "app.main"]
