import logging.config
import yaml
import os
import json
import time
from typing import Dict, Any

# Importa as classes dos agentes irmãos (a serem criadas)
# Assumindo que você terá classes básicas para cada agente
from .extraction_agent import ExtractionAgent
from .analysis_agent import AnalysisAgent
from .delivery_agent import DeliveryAgent
# from .memory_agent import MemoryAgent # (Opcional, se o workflow exigir)


# --- 1. Configuração do Logging (Carregamento) ---

# Define a função de inicialização de logs para ser chamada no main.py ou no startup do container
def initialize_logging(config_path='logging_config.yaml'):
    """Carrega a configuração de logging a partir de um arquivo YAML."""
    if not os.path.exists(config_path):
        print(f"ERRO CRÍTICO: Arquivo de configuração de logging não encontrado em {config_path}")
        return
        
    try:
        with open(config_path, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao carregar logging config: {e}")
        
# Inicialização dos logs (será movida para main.py no ambiente de produção)
# initialize_logging() 
logger = logging.getLogger('CoordinatorAgent')


# --- 2. Funções de Ajuda (Mantidas e Aperfeiçoadas) ---

def load_workflow_config(workflow_name: str) -> Dict[str, Any] | None:
    """Carrega o fluxo de trabalho dinâmico do diretório workflows/."""
    try:
        # Acessa o caminho a partir da raiz do projeto
        path = os.path.join(os.getcwd(), 'workflows', f'{workflow_name}.yaml')
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Usamos logging.error aqui, mas precisamos do task_id, vamos usar print para fins de demonstração
        print(f"ERRO: Workflow '{workflow_name}' não encontrado.")
        return None

def get_agent_instance(agent_name: str):
    """Retorna a instância da classe do agente pelo nome."""
    # Mapeamento do nome do agente no YAML para a classe Python
    mapping = {
        "ExtractionAgent": ExtractionAgent,
        "AnalysisAgent": AnalysisAgent,
        "DeliveryAgent": DeliveryAgent,
        # Adicione outros agentes aqui:
        # "MemoryAgent": MemoryAgent,
    }
    AgentClass = mapping.get(agent_name)
    if AgentClass:
        # Retorna uma nova instância do agente (pode precisar de injeção de dependência real)
        return AgentClass() 
    raise ValueError(f"Agente desconhecido no workflow: {agent_name}")


# --- 3. Lógica Principal do Coordenador ---

def process_task_from_api(task_payload: dict):
    """
    Recebe a tarefa do API Gateway, orquestra o fluxo de trabalho e gerencia o estado.
    """
    task_id = task_payload.get("task_id")
    user_request = task_payload.get("user_request")
    file_path = task_payload.get("file_path")
    
    # Define o contexto extra para o logger
    extra_data = {'task_id': task_id}
    
    logger.info("INÍCIO: Recebido do API Gateway. Arquivo: %s", file_path, extra=extra_data)
    
    # 2. Decisão de Fluxo de Trabalho (Decisão Simples baseada em um padrão)
    # Aqui, a lógica real usaria LLM ou Regras de Negócio para decidir o workflow
    if "fatura" in user_request.lower():
        workflow_name = "project_invoice_extract"
    else:
        workflow_name = "default_pdf_analysis"
        
    workflow_config = load_workflow_config(workflow_name)

    if not workflow_config:
        logger.error("Falha ao carregar workflow '%s'. Abortando.", workflow_name, extra=extra_data)
        # TODO: Notificar o sistema de status/API de erro.
        return
        
    logger.info("Fluxo de trabalho selecionado: %s", workflow_name, extra=extra_data)
    
    # 3. Execução do Pipeline Sequencial
    
    # Variável para rastrear o output entre os passos
    current_output = task_payload 
    
    try:
        # O workflow YAML deve ter uma lista de tarefas 'tasks_sequence'
        for step in workflow_config.get('tasks_sequence', []):
            agent_name = step['agent']
            command = step['command']
            
            logger.info("Executando passo: Agente: %s, Comando: %s", agent_name, command, extra=extra_data)
            
            # 3.1. Instanciar o Agente
            target_agent = get_agent_instance(agent_name)
            
            # 3.2. Chamar o método de execução do Agente (simulação)
            # Passamos o output do passo anterior e o contexto da solicitação
            
            # *** SIMULAÇÃO DE CHAMADA REAL ***
            
            # O Agente Coordenador passa o que o Agente precisa:
            # - O payload atual (output do passo anterior)
            # - O request original do usuário
            
            current_output = target_agent.execute(
                input_data=current_output, 
                user_request=user_request, 
                command=command,
                task_id=task_id
            )
            
            logger.info("Passo concluído. Saída do Agente %s: %s caracteres.", 
                        agent_name, len(str(current_output.get('output_data'))), extra=extra_data)

            # 3.3. (Opcional) Verificação de Erro Simples
            if current_output.get('status') == 'error':
                 raise Exception(f"Erro reportado pelo {agent_name}: {current_output.get('message')}")
            
        
        # 4. Sucesso Final
        final_result = current_output.get('output_data', 'Resultado final não formatado.')
        
        logger.info("FIM: Processamento de pipeline concluído com sucesso. Resultado final pronto.", extra=extra_data)
        
        # TODO: Notificar o sistema de status/API de sucesso e armazenar o 'final_result' no DB de status.
        
        return {"status": "success", "result": final_result}
        
    except Exception as e:
        logger.error("ERRO CRÍTICO no pipeline de task %s: %s", task_id, str(e), extra=extra_data)
        
        # TODO: Notificar o sistema de status/API de erro.
        # TODO: Implementar lógica de rollback ou limpeza de arquivos temporários.
        
        return {"status": "error", "message": str(e)}

# --- FIM do Agente Coordenador ---
