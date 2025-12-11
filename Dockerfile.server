# Arquivo: server/Dockerfile.server

# 1. Base Stage
FROM python:3.11-slim

# 2. Setup
WORKDIR /app

# Instala dependências do FastAPI
# Deve apontar diretamente para o arquivo no contexto (requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API para o contêiner
# Deve copiar o contexto inteiro (o conteúdo da pasta 'server')
COPY . /app/

# Expõe a porta e define o comando de execução
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]