# Arquivo: agents/analysis_agent.py
import logging
from typing import Dict, Any
import google.generativeai as genai
import os

logger = logging.getLogger('AnalysisAgent')

class AnalysisAgent:
    """
    Agente de Raciocínio (Core Logic). Analisa o contexto completo (extração + memória) 
    para formular uma resposta usando o LLM.
    """

    def __init__(self):
        # Inicialize o LLM (modelo e configurações) aqui.
        # Configura a chave da API do Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(model_name=os.getenv("LLM_MODEL", "gemini-pro"))
        logger.info("AnalysisAgent inicializado com o modelo Gemini: %s", os.getenv("LLM_MODEL", "gemini-pro"))

    def execute(self, input_data: Dict[str, Any], user_request: str, command: str, task_id: str) -> Dict[str, Any]:
        """Executa a tarefa de análise, usando o contexto e a requisição do usuário."""
        extra_data = {'task_id': task_id}
        
        if command == "generate_answer_from_context":
            # Assume que input_data.get('output_data') contém todos os dados relevantes (chunks + memória)
            combined_context = input_data.get('output_data', {})
            
            extracted_chunks = combined_context.get('extracted_chunks', [])
            search_results = combined_context.get('search_results', [])
            
            logger.info("Iniciando análise. Contexto de entrada: %d chunks extraídos, %d resultados de busca.", 
                        len(extracted_chunks), len(search_results), extra=extra_data)
            
            # Montar o prompt
            context_str = ""
            if extracted_chunks:
                context_str += "### Conteúdo do Documento Atual:\n" + "\n".join(extracted_chunks) + "\n\n"
            if search_results:
                context_str += "### Conhecimento Relevante da Base de Dados:\n"
                for res in search_results:
                    context_str += f"- {res.get('text', '')} (Fonte: {res.get('source', 'N/A')})\n"
                context_str += "\n"

            prompt = f"""
            Você é um assistente de IA especializado em análise de documentos.
            Baseado no contexto fornecido abaixo, responda à seguinte questão do usuário de forma concisa e precisa.
            Se a resposta não puder ser encontrada no contexto, informe isso.

            ---
            {context_str}
            ---

            Questão do Usuário: {user_request}

            Resposta:
            """
            
            try:
                # Chamar o LLM
                response = self.model.generate_content(prompt)
                final_answer = response.text
                logger.info("Análise concluída pelo LLM. Resultado final pronto para Delivery.", extra=extra_data)
            except Exception as e:
                logger.error("Erro ao chamar o LLM Gemini: %s", str(e), extra=extra_data)
                final_answer = "Desculpe, não foi possível gerar uma resposta devido a um erro interno."
            
            # Retorna o resultado para o DeliveryAgent
            return {
                "status": "processing",
                "output_data": final_answer,
                "message": "Analysis successful. Final result ready for formatting."
            }

        else:
            logger.warning("Comando desconhecido: %s", command, extra=extra_data)
            return {"status": "error", "message": f"Unknown command: {command}"}