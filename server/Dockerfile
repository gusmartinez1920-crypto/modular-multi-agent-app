# Arquivo: server/Dockerfile

# 1. Base Stage
FROM python:3.11-slim

# 2. Setup
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt /app/server/requirements.txt
RUN pip install --no-cache-dir -r /app/server/requirements.txt

# Copia o código da aplicação para dentro do contêiner
COPY . /app/server

# Expõe a porta e define o comando de execução
EXPOSE 8000
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]