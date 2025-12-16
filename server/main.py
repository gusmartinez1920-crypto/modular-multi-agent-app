# Arquivo: server/main.py
import os
import uuid
import json
import logging
import redis
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# --- Configuração ---
REDIS_HOST = os.getenv("REDIS_HOST", "message-broker")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
TASK_QUEUE_NAME = "task_queue"

# Diretórios compartilhados via volume do Docker
INPUT_DIR = "/app/data/input_pdfs"
OUTPUT_DIR = "/app/data/output_reports"

# Garante que os diretórios existam
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configura o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-gateway")

# --- Conexão com Redis ---
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    redis_client.ping()
    logger.info(f"Conectado ao Redis em {REDIS_HOST}:{REDIS_PORT}")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Não foi possível conectar ao Redis: {e}", exc_info=True)
    redis_client = None

# --- Modelo de Dados ---
class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None

# --- Inicialização da Aplicação ---
app = FastAPI(
    title="API Gateway para Sistema de Multiagentes",
    description="Recebe requisições de análise de documentos e as enfileira para o backend de agentes via Redis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints da API ---

@app.get("/", summary="Verificação de Saúde")
async def read_root():
    return {"message": "API Gateway está operacional."}

@app.post("/api/process-document", response_model=TaskStatus, summary="Processar um novo documento")
async def process_document(
    query: str = Form(...),
    file: UploadFile = File(...)
):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Serviço de fila indisponível (Redis).")
        
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Somente arquivos PDF são permitidos.")

    task_id = str(uuid.uuid4())
    saved_file_path = os.path.join(INPUT_DIR, f"{task_id}_{file.filename}")

    try:
        # Salva o arquivo PDF
        with open(saved_file_path, "wb") as buffer:
            buffer.write(await file.read())
        logger.info(f"Arquivo '{file.filename}' salvo em '{saved_file_path}' para a tarefa {task_id}.")

        # Cria a tarefa e a publica na fila do Redis
        task_payload = {
            "task_id": task_id,
            "user_request": query,
            "file_path": saved_file_path,
            "workflow_hint": "default_pdf_analysis"
        }
        
        redis_client.lpush(TASK_QUEUE_NAME, json.dumps(task_payload))
        logger.info(f"Tarefa {task_id} adicionada à fila '{TASK_QUEUE_NAME}'.")

    except Exception as e:
        logger.error(f"Erro ao processar o upload para a tarefa {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")

    return TaskStatus(task_id=task_id, status="PENDING")


@app.get("/api/task-status/{task_id}", response_model=TaskStatus, summary="Verificar o status de uma tarefa")
async def get_task_status(task_id: str):
    """
    Verifica o resultado de uma tarefa.
    Se um resultado existe, retorna SUCESSO. Senão, assume que está em processamento ou pendente.
    """
    output_file_path = os.path.join(OUTPUT_DIR, f"{task_id}.json")

    if os.path.exists(output_file_path):
        try:
            with open(output_file_path, "r") as f:
                result_data = json.load(f)
            
            os.remove(output_file_path)

            return TaskStatus(
                task_id=task_id,
                status="SUCCESS",
                result=result_data.get("report_content", "Conteúdo não encontrado.")
            )
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo de resultado para a tarefa {task_id}: {e}", exc_info=True)
            return TaskStatus(task_id=task_id, status="FAILED", error=str(e))
    else:
        # Se o arquivo de saída não existe, a tarefa está na fila ou sendo processada.
        # Uma lógica mais granular poderia consultar um status no Redis, 
        # mas isso exigiria que o worker atualizasse o status,
        # o que foge do escopo desta refatoração inicial.
        return TaskStatus(task_id=task_id, status="PROCESSING")