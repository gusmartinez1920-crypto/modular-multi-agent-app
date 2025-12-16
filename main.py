# Arquivo: main.py
import logging.config
import yaml
import os
import time
import json
import redis
from dotenv import load_dotenv

# Importa a função principal do Coordenador
from agents.coordinator_agent import process_task_from_api

# --- CONFIGURAÇÃO ---
REDIS_HOST = os.getenv("REDIS_HOST", "message-broker")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
TASK_QUEUE_NAME = "task_queue"

# 1. Função de Inicialização de Logs
def initialize_logging(config_path='logging_config.yaml'):
    """Carrega a configuração de logging e garante o diretório de logs."""
    log_dir = 'data/logs'
    os.makedirs(log_dir, exist_ok=True)
    
    if not os.path.exists(config_path):
        print(f"ERRO CRÍTICO: Arquivo de logging não encontrado em {config_path}. Usando logs padrão.")
        return
        
    try:
        with open(config_path, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao carregar logging config: {e}")

# 2. Inicialização do Motor do Backend
def start_agent_backend():
    load_dotenv()
    initialize_logging()
    
    root_logger = logging.getLogger()
    root_logger.info("Sistema de Multiagentes Inicializado.")

    # Conexão com Redis
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        redis_client.ping()
        root_logger.info(f"Conectado ao Redis em {REDIS_HOST}:{REDIS_PORT}")
    except redis.exceptions.ConnectionError as e:
        root_logger.error(f"Não foi possível conectar ao Redis. O sistema será encerrado: {e}", exc_info=True)
        return

    print(f"\n--- Modo de Escuta Ativado na fila '{TASK_QUEUE_NAME}' (Ctrl+C para sair) ---")
    
    try:
        while True:
            # Espera bloqueante por uma nova tarefa na fila
            # BRPOP retorna uma tupla (nome_da_fila, item) ou None se o timeout for atingido
            task_item = redis_client.brpop(TASK_QUEUE_NAME)
            
            if not task_item:
                continue

            # O item é retornado como bytes, então decodificamos e carregamos o JSON
            task_payload_str = task_item[1].decode('utf-8')
            payload = json.loads(task_payload_str)
            
            task_id = payload.get("task_id", "ID não encontrado")
            root_logger.info(f"Nova tarefa recebida da fila: {task_id}")

            try:
                # Executa o processo multiagentes
                result = process_task_from_api(payload)
                
                # Reporta o resultado
                root_logger.info("Resultado da Tarefa %s: Status: %s", 
                                 task_id, result.get('status', 'desconhecido'))

            except Exception as e:
                root_logger.error("Erro ao processar a tarefa %s: %s", task_id, e, exc_info=True)
                # Opcional: mover para uma fila de "falhas" em vez de descartar
                # redis_client.lpush("failed_queue", task_payload_str)


    except KeyboardInterrupt:
        root_logger.warning("Motor de Agentes Desligado pelo Usuário.")
    except Exception as e:
        root_logger.error("Erro fatal no loop principal: %s", str(e), exc_info=True)
    finally:
        root_logger.info("Shutdown completo.")


# --- PONTO DE EXECUÇÃO ---

if __name__ == "__main__":
    start_agent_backend()