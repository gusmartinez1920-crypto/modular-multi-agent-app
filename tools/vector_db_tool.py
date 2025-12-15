# Arquivo: tools/vector_db_tool.py
# Arquivo: tools/vector_db_tool.py
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger('VectorDBTool')

# O caminho para salvar a base de dados Chroma
DB_PATH = "data/vector_store"
COLLECTION_NAME = "pdf_analysis"

class VectorDBTool:
    """
    Ferramenta para interagir com a base de dados vetorial (ChromaDB).
    Utilizada para RAG (Retrieval Augmented Generation).
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # Inicializa o cliente ChromaDB
        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        # Inicializa o modelo de embeddings
        self.model = SentenceTransformer(model_name)
        
        # Obtém ou cria a coleção
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=None  # Vamos fornecer os embeddings manualmente
        )
        logger.info("Cliente ChromaDB inicializado e coleção '%s' carregada.", COLLECTION_NAME)

    def add_documents(self, texts: List[str], task_id: str, document_id: str) -> None:
        """
        Adiciona uma lista de textos à coleção ChromaDB.
        """
        extra_data = {'task_id': task_id}
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False).tolist()
            
            # Gera IDs únicos para cada documento
            doc_ids = [f"{task_id}-{document_id}-{i}" for i in range(len(texts))]
            
            metadatas = [{
                "source": document_id,
                "task": task_id
            } for _ in texts]
            
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=doc_ids
            )
            
            logger.info("Adicionado %d documentos à coleção '%s'.", len(texts), COLLECTION_NAME, extra=extra_data)
        except Exception as e:
            logger.error("Falha ao adicionar documentos ao ChromaDB: %s", str(e), extra=extra_data)
            raise RuntimeError(f"ChromaDB add failure: {e}")

    def search(self, query: str, task_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca por documentos relevantes na coleção com base em uma consulta.
        """
        extra_data = {'task_id': task_id}
        
        try:
            query_embedding = self.model.encode([query], convert_to_tensor=False).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Formata os resultados para o formato esperado
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "text": doc,
                        "metadata": results['metadatas'][0][i]
                    })
            
            logger.info("Busca concluída. Retornando %d resultados.", len(formatted_results), extra=extra_data)
            return formatted_results
            
        except Exception as e:
            logger.error("Falha na busca no ChromaDB: %s", str(e), extra=extra_data)
            return [] # Retorna lista vazia em caso de falha