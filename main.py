# Arquivo: main.py
import logging.config
import yaml
import os
import time
from dotenv import load_dotenv

# Importa a função principal do Coordenador
from agents.coordinator_agent import process_task_from_api 

# --- CONFIGURAÇÃO ---

# 1. Função de Inicialização de Logs (Recomendado ser no main.py)
def initialize_logging(config_path='logging_config.yaml'):
    """Carrega a configuração de logging e garante o diretório de logs."""
    
    # Garante que a pasta 'data/logs' exista no volume compartilhado
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
    # Carregar variáveis de ambiente (chaves de API, etc.)
    load_dotenv()
    
    # Inicializar o sistema de logging
    initialize_logging()
    
    # Obter o logger raiz para mensagens de status
    root_logger = logging.getLogger()
    root_logger.info("Sistema de Multiagentes Inicializado com Sucesso.")
    root_logger.info("Aguardando tarefas do API Gateway...")

    # --- SIMULAÇÃO DA ESCUTA DE TAREFAS ---
    
    # Em um sistema real (e escalável), este loop faria o seguinte:
    # 1. Conectar a um Message Broker (RabbitMQ, Redis, Kafka)
    # 2. Entrar em um loop infinito, escutando por novas mensagens na fila.
    
    print("\n--- Modo de Escuta Ativado (Ctrl+C para sair) ---")
    
    # EXEMPLO DE TESTE E ESCUTA SÍNCRONA:
    # Para demonstração, vamos apenas simular que uma tarefa foi recebida:
    
    # Estrutura do payload recebido do API Gateway
    mock_payload = {
        "task_id": "T-SIMULACAO-001",
        "user_request": "Analise o relatório financeiro do 3º trimestre e summarize os riscos principais.",
        # Este path existe no volume compartilhado (./data)
        "file_path": "data/input_pdfs/relatorio_mock.pdf", 
        "workflow_hint": "finance_analysis"
    }

    try:
        # AQUI O MOTOR CHAMA O COORDENADOR:
        # Nota: O 'task_id' precisa ser injetado para fins de logging e rastreio.
        # Passamos o payload diretamente para a função do coordenador
        
        # Simulação de um loop de escuta infinito
        while True:
            # Em produção, este bloco seria substituído pela leitura da fila
            if time.time() % 10 < 1: # Tenta processar a cada 10 segundos para simular
                root_logger.info("Simulando recepção de nova tarefa...")
                
                # Executa o processo multiagentes
                result = process_task_from_api(mock_payload)
                
                # Reporta o resultado (em produção, enviaria para o DB de Status)
                root_logger.info("Resultado da Tarefa %s: Status: %s", 
                                 mock_payload['task_id'], result['status'])
                
                # Evita sobrecarga de logs
                time.sleep(5) 
            
            time.sleep(1) # Espera 1 segundo

    except KeyboardInterrupt:
        root_logger.warning("Motor de Agentes Desligado pelo Usuário.")
    except Exception as e:
        root_logger.error("Erro fatal no loop principal: %s", str(e))
    finally:
        root_logger.info("Shutdown completo.")


# --- PONTO DE EXECUÇÃO ---

if __name__ == "__main__":
    start_agent_backend()