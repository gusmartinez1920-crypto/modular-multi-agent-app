# Arquivo: agents/delivery_agent.py
import logging
import json
from typing import Dict, Any, Union

logger = logging.getLogger('DeliveryAgent')

class DeliveryAgent:
    """
    Agente de Entrega e Formatação de Saída.
    Responsável por receber a resposta final do AnalysisAgent e formatá-la 
    no padrão de entrega (JSON/Markdown) para o sistema externo (API).
    """

    def __init__(self):
        # O DeliveryAgent geralmente não precisa de ferramentas externas complexas
        pass

    def execute(self, input_data: Dict[str, Any], user_request: str, command: str, task_id: str) -> Dict[str, Union[str, Dict[str, Any]]]:
        """
        Executa a tarefa de entrega. O input_data contém o resultado da análise.
        """
        extra_data = {'task_id': task_id}
        
        # O resultado da análise é o output_data da etapa anterior (AnalysisAgent)
        analysis_result = input_data.get('output_data', "Resultado não encontrado.")
        
        if command == "format_final_report":
            
            logger.info("Iniciando formatação do relatório final.", extra=extra_data)
            
            # --- Lógica de Formatação ---
            
            # Aqui, idealmente, você usaria Pydantic ou JSON Schema para formatar a saída.
            
            final_json_report = {
                "task_id": task_id,
                "user_query": user_request,
                "timestamp": logging.Formatter('%Y-%m-%d %H:%M:%S').formatTime(logging.LogRecord(None, None, None, None, None, None)),
                "status": "COMPLETED",
                "result_type": "markdown",
                "report_content": analysis_result
            }
            
            final_json_string = json.dumps(final_json_report, indent=2)
            
            logger.info("Relatório final formatado em JSON. Tamanho: %d caracteres.", len(final_json_string), extra=extra_data)
            
            # Retorna o resultado final, formatado e pronto para o sistema externo
            return {
                "status": "success",
                "output_data": final_json_report,
                "message": "Final report formatted and ready for API delivery."
            }

        else:
            logger.warning("Comando desconhecido: %s", command, extra=extra_data)
            return {"status": "error", "message": f"Unknown command: {command}"}