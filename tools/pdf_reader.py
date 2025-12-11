# Arquivo: tools/pdf_reader.py
from pypdf import PdfReader
from typing import List, Dict
import logging
import os

logger = logging.getLogger('PDFReaderTool')

class PDFReaderTool:
    """
    Ferramenta para ler documentos PDF e extrair seu conteúdo textual.
    """

    @staticmethod
    def read_pdf_content(file_path: str, task_id: str) -> str:
        """
        Lê o texto completo de um arquivo PDF.
        """
        extra_data = {'task_id': task_id}
        
        if not os.path.exists(file_path):
            logger.error("Arquivo não encontrado no caminho: %s", file_path, extra=extra_data)
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        text = ""
        try:
            reader = PdfReader(file_path)
            
            # Extrai o texto de todas as páginas
            for page in reader.pages:
                text += page.extract_text() or ""
                
            logger.info("Extração de texto concluída. Total de caracteres: %d", len(text), extra=extra_data)
            return text
            
        except Exception as e:
            logger.error("Erro ao ler o PDF %s: %s", file_path, str(e), extra=extra_data)
            raise RuntimeError(f"Failed to read PDF: {e}")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Divide o texto longo em pedaços (chunks) com sobreposição.
        (Essencial para RAG e MemoryAgent)
        """
        
        # Implementação básica de chunking (pode ser substituída por frameworks como LangChain/LlamaIndex)
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move o ponteiro de início com sobreposição
            start += chunk_size - overlap
            if start < 0:
                start = 0
                
        return chunks