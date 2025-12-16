# Arquivo: agents/delivery_agent.py
import logging
import json
import os
from typing import Dict, Any, Union

logger = logging.getLogger('DeliveryAgent')

# Diretório para salvar os relatórios finais, acessível pelo API Gateway
OUTPUT_DIR = "/app/data/output_reports"

class DeliveryAgent:
    """
    Agente de Entrega e Formatação de Saída.
    Responsável por receber a resposta final do AnalysisAgent e formatá-la 
    no padrão de entrega, salvando o resultado para a API.
    """

    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def execute(self, input_data: Dict[str, Any], user_request: str, command: str, task_id: str) -> Dict[str, Union[str, Dict[str, Any]]]:
        """
        Executa a tarefa de entrega. O input_data contém o resultado da análise.
        """
        extra_data = {'task_id': task_id}
        
        analysis_result = input_data.get('output_data', "Resultado não encontrado.")
        
        if command == "format_final_report":
            
            logger.info("Iniciando formatação e salvamento do relatório final.", extra=extra_data)
            
            final_json_report = {
                "task_id": task_id,
                "user_query": user_request,
                "status": "COMPLETED",
                "report_content": analysis_result
            }
            
            output_file_path = os.path.join(OUTPUT_DIR, f"{task_id}.json")
            
            try:
                with open(output_file_path, "w") as f:
                    json.dump(final_json_report, f, indent=2)
                
                logger.info(f"Relatório final da tarefa {task_id} salvo em {output_file_path}.", extra=extra_data)

                return {
                    "status": "success",
                    "output_data": final_json_report,
                    "message": f"Final report saved to {output_file_path}."
                }
            except Exception as e:
                logger.error(f"Falha ao salvar o relatório final para a tarefa {task_id}: {e}", extra=extra_data)
                return {"status": "error", "message": f"Failed to save report: {e}"}

        else:
            logger.warning("Comando desconhecido: %s", command, extra=extra_data)
            return {"status": "error", "message": f"Unknown command: {command}"}