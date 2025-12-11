# Arquivo: tools/vector_db_tool.py
import chromadb
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger('VectorDBTool')

# O caminho deve ser o mesmo usado no volume compartilhado do Docker
DB_PATH = "data/vector_store" 

class VectorDBTool:
    """
    Ferramenta para interagir com a base de dados vetorial (ChromaDB).
    Utilizada para RAG (Retrieval Augmented Generation).
    """

    def __init__(self, collection_name: str = "document_collection"):
        # Inicializa o cliente do ChromaDB
        self.client = chromadb.PersistentClient(path=DB_PATH)
        # Cria ou obtém a coleção
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info("Vector DB inicializado em %s com coleção: %s", DB_PATH, collection_name)

    def add_documents(self, texts: List[str], task_id: str, document_id: str) -> None:
        """
        Adiciona uma lista de textos à base de dados, criando embeddings.
        """
        extra_data = {'task_id': task_id}
        
        # Cria IDs únicos para cada chunk
        ids = [f"{document_id}-{i}" for i in range(len(texts))]
        
        try:
            self.collection.add(
                documents=texts,
                metadatas=[{"source": document_id, "task": task_id}] * len(texts),
                ids=ids
            )
            logger.info("Adicionado %d documentos à coleção.", len(texts), extra=extra_data)
        except Exception as e:
            logger.error("Falha ao adicionar documentos ao Vector DB: %s", str(e), extra=extra_data)
            raise RuntimeError(f"Vector DB add failure: {e}")

    def search(self, query: str, n_results: int = 5, task_id: str) -> List[Dict[str, Any]]:
        """
        Busca por documentos relevantes na base de dados com base em uma consulta.
        """
        extra_data = {'task_id': task_id}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Formata a saída para ser facilmente consumida pelo Agente de Análise
            formatted_results = []
            if results.get('documents') and results['documents'][0]:
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    formatted_results.append({
                        "text": doc,
                        "source": meta.get('source'),
                        "task": meta.get('task')
                    })
                    
            logger.info("Busca concluída. Retornando %d resultados.", len(formatted_results), extra=extra_data)
            return formatted_results
            
        except Exception as e:
            logger.error("Falha na busca no Vector DB: %s", str(e), extra=extra_data)
            return [] # Retorna lista vazia em caso de falha


#