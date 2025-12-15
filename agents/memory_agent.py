# Arquivo: agents/memory_agent.py
import logging
from typing import Dict, Any, List
import uuid

# Importa a ferramenta de Vector DB que criamos
from tools.vector_db_tool import VectorDBTool 

logger = logging.getLogger('MemoryAgent')

class MemoryAgent:
    """
    Agente especialista em Gestão de Conhecimento e RAG. 
    Responsável por armazenar e recuperar chunks de texto usando o VectorDBTool.
    """

    def __init__(self):
        # O MemoryAgent deve ter uma instância da ferramenta de DB Vetorial
        self.db_tool = VectorDBTool()
        logger.info("MemoryAgent inicializado com VectorDBTool.")

    def execute(self, input_data: Dict[str, Any], user_request: str, command: str, task_id: str) -> Dict[str, Any]:
        """
        Executa comandos de memória (armazenamento ou busca) conforme 
        instruído pelo Coordenador.
        """
        extra_data = {'task_id': task_id}
        
        # O 'document_id' será usado para rastrear a origem dos dados
        document_id = input_data.get('file_path', f"temp-doc-{uuid.uuid4()}")
        
        # --- Comando 1: BUSCA DE CONHECIMENTO (RAG) ---
        if command == "search_knowledge_base":
            
            # O MemoryAgent precisa saber o que buscar. Ele busca pelo user_request e 
            # também armazena os chunks recém-extraídos para uso posterior.

            # 1. Recupera os chunks extraídos na etapa anterior
            extracted_chunks: List[str] = input_data.get('output_data', [])
            
            # 2. Armazena os novos chunks antes de buscar (para que a busca futura os inclua)
            if extracted_chunks:
                try:
                    self.db_tool.add_documents(extracted_chunks, task_id, document_id)
                    logger.info("Chunks do documento atual adicionados ao Vector DB.", extra=extra_data)
                except Exception as e:
                    logger.warning("Falha ao persistir chunks: %s", str(e), extra=extra_data)

            # 3. Realiza a busca baseada na requisição do usuário
            query = user_request
            logger.info("Iniciando busca no Vector DB com a query: %s", query, extra=extra_data)
            
            # Executa a busca
            search_results = self.db_tool.search(query, n_results=10, task_id=task_id)
            
            # Combina os dados de entrada com os resultados da busca
            # Esta combinação será a entrada para o AnalysisAgent (memory_and_extraction_data)
            combined_context = {
                "extracted_chunks": extracted_chunks,  # Chunks do documento que está sendo processado
                "search_results": search_results,      # Chunks relevantes de documentos passados/outros
                "user_request": user_request
            }
            
            logger.info("Busca e consolidação de contexto concluídas. Total de chunks recuperados: %d", 
                        len(search_results), extra=extra_data)

            return {
                "status": "processing",
                "output_data": combined_context,
                "message": "Knowledge retrieved and context consolidated."
            }
        
        # --- Comando 2: OUTROS COMANDOS DE GESTÃO DE MEMÓRIA (futuro) ---
        elif command == "store_final_report":
            # Lógica para armazenar o relatório final no DB ou outra coleção
            logger.warning("Comando 'store_final_report' não implementado.", extra=extra_data)
            return {"status": "processing", "output_data": input_data.get('output_data')}
        
        # --- Comando Desconhecido ---
        else:
            logger.warning("Comando desconhecido: %s", command, extra=extra_data)
            return {"status": "error", "message": f"Unknown command: {command}"}