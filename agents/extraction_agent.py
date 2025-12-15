import logging
from typing import Dict, Any
from tools.pdf_reader import PDFReaderTool # Importar a ferramenta

logger = logging.getLogger('ExtractionAgent')

class ExtractionAgent:
    """
    Especialista em processamento de documentos. Extrai e pré-processa dados de PDFs, 
    transformando-os em chunks de texto para uso posterior.
    """

    def __init__(self):
        self.pdf_reader_tool = PDFReaderTool() # Instanciar a ferramenta

    def execute(self, input_data: Dict[str, Any], user_request: str, command: str, task_id: str) -> Dict[str, Any]:
        """Executa a tarefa de extração, seguindo o comando do Coordenador."""
        extra_data = {'task_id': task_id}
        
        if command == "parse_and_chunk_pdf":
            file_path = input_data.get('file_path')
            logger.info("Iniciando extração do PDF em: %s", file_path, extra=extra_data)
            
            try:
                # 1. Ler o conteúdo completo do PDF
                full_text = self.pdf_reader_tool.read_pdf_content(file_path, task_id)
                
                # 2. Chunk o texto
                extracted_chunks = self.pdf_reader_tool.chunk_text(full_text)
                
                logger.info("Extração e chunking concluídos. %d chunks gerados.", len(extracted_chunks), extra=extra_data)
                
                # Retorna o resultado para o próximo agente (MemoryAgent no YAML)
                return {
                    "status": "processing",
                    "output_data": extracted_chunks,
                    "file_path": file_path,
                    "message": "Data successfully extracted and chunked."
                }
            except Exception as e:
                logger.error("Erro durante a extração e chunking do PDF: %s", str(e), extra=extra_data)
                return {"status": "error", "message": f"PDF extraction and chunking failed: {str(e)}"}

        else:
            logger.warning("Comando desconhecido: %s", command, extra=extra_data)
            return {"status": "error", "message": f"Unknown command: {command}"}