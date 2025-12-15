# Arquivo: main.py
import logging.config
import yaml
import os
import time
import json
from dotenv import load_dotenv

# Importa a função principal do Coordenador
from agents.coordinator_agent import process_task_from_api 

# --- CONFIGURAÇÃO ---
QUEUE_DIR = 'data/queue'

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
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Inicializar o sistema de logging
    initialize_logging()
    
    # Garantir que o diretório da fila exista
    os.makedirs(QUEUE_DIR, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.info("Sistema de Multiagentes Inicializado com Sucesso.")
    root_logger.info("Aguardando tarefas no diretório: %s", QUEUE_DIR)

    print(f"\n--- Modo de Escuta Ativado em '{QUEUE_DIR}' (Ctrl+C para sair) ---")
    
    try:
        while True:
            # Lista os arquivos de tarefa no diretório da fila
            tasks = [f for f in os.listdir(QUEUE_DIR) if f.endswith('.json')]
            
            if not tasks:
                time.sleep(2) # Espera se não houver tarefas
                continue

            for task_file in tasks:
                file_path = os.path.join(QUEUE_DIR, task_file)
                
                try:
                    with open(file_path, 'r') as f:
                        payload = json.load(f)
                    
                    root_logger.info("Nova tarefa recebida: %s", payload.get("task_id", "ID não encontrado"))
                    
                    # Executa o processo multiagentes
                    result = process_task_from_api(payload)
                    
                    # Reporta o resultado
                    root_logger.info("Resultado da Tarefa %s: Status: %s", 
                                     payload.get('task_id', 'N/A'), result.get('status', 'desconhecido'))

                except json.JSONDecodeError as e:
                    root_logger.error("Erro ao decodificar JSON da tarefa %s: %s", task_file, e)
                except Exception as e:
                    root_logger.error("Erro ao processar a tarefa %s: %s", task_file, e)
                finally:
                    # Remove o arquivo da tarefa após o processamento (bem-sucedido ou falho)
                    os.remove(file_path)
                    root_logger.info("Tarefa %s removida da fila.", task_file)

    except KeyboardInterrupt:
        root_logger.warning("Motor de Agentes Desligado pelo Usuário.")
    except Exception as e:
        root_logger.error("Erro fatal no loop principal: %s", str(e), exc_info=True)
    finally:
        root_logger.info("Shutdown completo.")


# --- PONTO DE EXECUÇÃO ---

if __name__ == "__main__":
    start_agent_backend()