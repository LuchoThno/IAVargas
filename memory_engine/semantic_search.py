"""
Semantic Search - Búsqueda Semántica Vectorizada
===============================================
IA Local Vargas - Memory Engine
Sistema de búsqueda semántica optimizado con operaciones vectorizadas
"""

import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from . import embedding_engine
from . import config

logger = logging.getLogger(__name__)


class SemanticSearch:
    """
    Motor de búsqueda semántica con operaciones vectorizadas
    """
    
    def __init__(
        self,
        use_faiss: bool = True,
        batch_size: int = 32,
        min_score: float = 0.0
    ):
        """
        Inicializa el motor de búsqueda semántica
        
        Args:
            use_faiss: Usar FAISS si está disponible
            batch_size: Tamaño de batch para embeddings
            min_score: Score mínimo de similaridad
        """
        self.use_faiss = use_faiss
        self.batch_size = batch_size
        self.min_score = min_score
        
        # Datos indexados
        self._embeddings = None
        self._texts = []
        self._metadata = []
        
        # Try to use vector index
        self._vector_index = None
    
    def index_documents(
        self,
        texts: List[str],
        metadata: Optional[List[Dict]] = None,
        batch_size: Optional[int] = None
    ):
        """
        Indexa documentos para búsqueda
        
        Args:
            texts: Lista de textos a indexar
            metadata: Metadatos opcionales para cada texto
            batch_size: Tamaño de batch
        """
        if not texts:
            logger.warning("No hay textos para indexar")
            return
        
        batch_size = batch_size or self.batch_size
        
        logger.info(f"Indexando {len(texts)} documentos...")
        
        # Generar embeddings en batches
        self._embeddings = embedding_engine.embed_batch(
            texts, 
            batch_size=batch_size,
            normalize=True
        )
        
        self._texts = texts
        self._metadata = metadata or [{} for _ in texts]
        
        logger.info(f"Indexados {len(texts)} documentos (dimensión: {self._embeddings.shape})")
    
    def search(
        self,
        query: str,
        k: int = 5,
        min_score: Optional[float] = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca documentos similares a la query
        
        Args:
            query: Texto de búsqueda
            k: Número de resultados
            min_score: Score mínimo (opcional)
            filter_metadata: Filtrar por metadatos (opcional)
            
        Returns:
            Lista de resultados ordenados por relevancia
        """
        if not self._texts or self._embeddings is None:
            logger.warning("No hay documentos indexados")
            return []
        
        # Generar embedding de la query
        query_embedding = embedding_engine.embed(query, normalize=True)
        
        # Calcular similaridades de forma vectorizada
        scores = self._compute_similarities_vectorized(query_embedding)
        
        # Filtrar por score mínimo
        min_score = min_score or self.min_score
        
        # Crear lista de resultados
        results = []
        for i, score in enumerate(scores):
            if score >= min_score:
                # Filtrar por metadatos si se especifica
                if filter_metadata:
                    metadata = self._metadata[i]
                    match = all(
                        metadata.get(k) == v 
                        for k, v in filter_metadata.items()
                    )
                    if not match:
                        continue
                
                results.append({
                    "text": self._texts[i],
                    "score": float(score),
                    "index": i,
                    "metadata": self._metadata[i]
                })
        
        # Ordenar por score descendente
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tomar los top-k
        return results[:k]
    
    def _compute_similarities_vectorized(
        self,
        query_embedding: np.ndarray
    ) -> np.ndarray:
        """
        Calcula similaridades coseno de forma vectorizada
        
        Args:
            query_embedding: Embedding de la query
            
        Returns:
            Array de scores de similaridad
        """
        if self._embeddings is None or len(self._texts) == 0:
            return np.array([])
        
        # Embeddings ya están normalizados, solo producto punto
        # query: (dim,), embeddings: (n, dim)
        # Resultado: (n,)
        similarities = np.dot(self._embeddings, query_embedding)
        
        return similarities
    
    def search_batch(
        self,
        queries: List[str],
        k: int = 5,
        min_score: Optional[float] = None
    ) -> List[List[Dict]]:
        """
        Busca múltiples queries de forma eficiente
        
        Args:
            queries: Lista de queries
            k: Resultados por query
            min_score: Score mínimo
            
        Returns:
            Lista de listas de resultados
        """
        if not queries:
            return []
        
        min_score = min_score or self.min_score
        
        # Generar embeddings de todas las queries
        query_embeddings = embedding_engine.embed_batch(
            queries,
            batch_size=len(queries),
            normalize=True
        )
        
        # Calcular matriz de similaridades (vectorizada)
        # query_embeddings: (n_queries, dim)
        # self._embeddings: (n_docs, dim)
        # resultado: (n_queries, n_docs)
        similarity_matrix = np.dot(
            query_embeddings,
            self._embeddings.T
        )
        
        # Procesar cada query
        all_results = []
        
        for i, query in enumerate(queries):
            scores = similarity_matrix[i]
            
            # Crear resultados para esta query
            results = []
            for j, score in enumerate(scores):
                if score >= min_score:
                    results.append({
                        "text": self._texts[j],
                        "score": float(score),
                        "index": j,
                        "metadata": self._metadata[j]
                    })
            
            # Ordenar y limitar
            results.sort(key=lambda x: x["score"], reverse=True)
            all_results.append(results[:k])
        
        return all_results
    
    def get_similar(
        self,
        text: str,
        k: int = 5,
        exclude_index: Optional[int] = None
    ) -> List[Dict]:
        """
        Encuentra textos similares a uno dado
        
        Args:
            text: Texto de referencia
            k: Número de resultados
            exclude_index: Índice a excluir
            
        Returns:
            Lista de textos similares
        """
        results = self.search(text, k=k + 1)  # +1 para excluir
        
        # Excluir el texto de referencia si está indexado
        if exclude_index is not None:
            results = [r for r in results if r["index"] != exclude_index]
            results = results[:k]
        
        return results
    
    def add_documents(
        self,
        texts: List[str],
        metadata: Optional[List[Dict]] = None,
        batch_size: Optional[int] = None
    ):
        """
        Añade documentos al índice existente
        
        Args:
            texts: Textos a añadir
            metadata: Metadatos
            batch_size: Tamaño de batch
        """
        if not texts:
            return
        
        batch_size = batch_size or self.batch_size
        
        # Generar embeddings
        new_embeddings = embedding_engine.embed_batch(
            texts,
            batch_size=batch_size,
            normalize=True
        )
        
        # Concatenar con embeddings existentes
        if self._embeddings is not None:
            self._embeddings = np.vstack([self._embeddings, new_embeddings])
        else:
            self._embeddings = new_embeddings
        
        # Añadir textos y metadatos
        self._texts.extend(texts)
        metadata = metadata or [{} for _ in texts]
        self._metadata.extend(metadata)
        
        logger.info(f"Añadidos {len(texts)} documentos al índice")
    
    def clear(self):
        """Limpia el índice"""
        self._embeddings = None
        self._texts = []
        self._metadata = []
        logger.info("Índice de búsqueda limpiado")
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del índice"""
        return {
            "num_documents": len(self._texts),
            "embedding_dim": self._embeddings.shape[1] if self._embeddings is not None else 0,
            "total_embeddings": len(self._texts)
        }


# Instancia global
_search_engine = None


def get_search_engine() -> SemanticSearch:
    """Obtiene el motor de búsqueda semántica global"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearch()
    return _search_engine


def search_semantic(
    query: str,
    texts: List[str],
    k: int = 5,
    batch_size: int = 32,
    min_score: float = 0.0
) -> List[Dict]:
    """
    Función de conveniencia para búsqueda semántica
    
    Args:
        query: Query de búsqueda
        texts: Lista de textos a buscar
        k: Número de resultados
        batch_size: Tamaño de batch
        min_score: Score mínimo
        
    Returns:
        Lista de resultados
    """
    engine = SemanticSearch(batch_size=batch_size, min_score=min_score)
    engine.index_documents(texts)
    return engine.search(query, k=k)


def search_with_metadata(
    query: str,
    documents: List[Dict],
    text_field: str = "text",
    metadata_fields: Optional[Dict] = None,
    k: int = 5,
    min_score: float = 0.0
) -> List[Dict]:
    """
    Búsqueda semántica con metadatos
    
    Args:
        query: Query de búsqueda
        documents: Lista de documentos con texto y metadatos
        text_field: Campo que contiene el texto
        metadata_fields: Campos adicionales a incluir en metadatos
        k: Número de resultados
        min_score: Score mínimo
        
    Returns:
        Lista de resultados con metadatos
    """
    # Extraer textos y metadatos
    texts = [doc.get(text_field, "") for doc in documents]
    
    # Preparar metadatos
    metadata = []
    for doc in documents:
        meta = {k: v for k, v in doc.items() if k != text_field}
        if metadata_fields:
            meta = {k: doc.get(k) for k in metadata_fields}
        metadata.append(meta)
    
    # Crear motor y buscar
    engine = SemanticSearch(min_score=min_score)
    engine.index_documents(texts, metadata)
    
    return engine.search(query, k=k)


# Funciones de compatibilidad con código existente
def search_documents_semantic(
    query: str,
    documents: Dict[str, str],
    n_results: int = 3,
    min_score: float = 0.3
) -> List[Dict]:
    """
    Búsqueda semántica en documentos (compatibilidad)
    
    Args:
        query: Query
        documents: Diccionario {filename: text}
        n_results: Número de resultados
        min_score: Score mínimo
        
    Returns:
        Lista de resultados
    """
    # Preparar documentos
    texts = []
    sources = []
    
    for filename, text in documents.items():
        # Chunking
        from .text_chunker import chunk_text
        chunks = chunk_text(text)
        
        for chunk in chunks:
            texts.append(chunk)
            sources.append(filename)
    
    if not texts:
        return []
    
    # Buscar
    results = search_semantic(
        query=query,
        texts=texts,
        k=n_results * 3,  # Más resultados para filtrar por fuente
        min_score=min_score
    )
    
    # Filtrar por fuente y limitar
    seen_sources = set()
    final_results = []
    
    for r in results:
        source = r.get("metadata", {}).get("source", "")
        
        # Limitar a un resultado por fuente
        if source not in seen_sources or len(final_results) < n_results:
            final_results.append(r)
            seen_sources.add(source)
        
        if len(final_results) >= n_results:
            break
    
    return final_results

