"""
Embedding Engine - Motor de Embeddings
=====================================
IA Local Vargas - Memory Engine
Sistema de embeddings optimizado con lazy loading y batching
"""

import logging
from typing import List, Union, Optional
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

from . import config

logger = logging.getLogger(__name__)

# Modelo global (lazy loading)
_model = None
_model_name = None


def get_model(force_reload: bool = False) -> SentenceTransformer:
    """
    Obtiene el modelo de embeddings con lazy loading
    
    Args:
        force_reload: Si True, fuerza la recarga del modelo
        
    Returns:
        Instancia del modelo SentenceTransformer
    """
    global _model, _model_name
    
    if _model is None or force_reload:
        logger.info(f"Cargando modelo de embeddings: {config.EMBEDDING_MODEL}")
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
        _model_name = config.EMBEDDING_MODEL
        logger.info(f"Modelo '{_model_name}' cargado correctamente")
    
    return _model


def embed(text: str, normalize: bool = True) -> np.ndarray:
    """
    Genera un embedding para un texto
    
    Args:
        text: Texto a embeber
        normalize: Si True, normaliza el vector
        
    Returns:
        Vector numpy con el embedding
    """
    model = get_model()
    
    # Usar encode con convert_to_numpy directamente
    embedding = model.encode(
        text, 
        convert_to_numpy=True,
        normalize_embeddings=normalize,
        show_progress_bar=False
    )
    
    return embedding


def embed_batch(
    texts: List[str], 
    batch_size: int = 32,
    normalize: bool = True,
    show_progress: bool = True
) -> np.ndarray:
    """
    Genera embeddings para una lista de textos de forma optimizada
    
    Args:
        texts: Lista de textos a embeber
        batch_size: Tamaño de batch para procesamiento
        normalize: Si True, normaliza los vectores
        show_progress: Si True, muestra barra de progreso
        
    Returns:
        Matriz numpy con los embeddings (n_texts, embedding_dim)
    """
    if not texts:
        return np.array([])
    
    model = get_model()
    
    # Procesar en batches para mejor rendimiento
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
        show_progress_bar=show_progress,
        parallel_backend='threading'
    )
    
    return embeddings


def embed_texts_optimized(
    texts: List[str],
    batch_size: int = 32,
    max_workers: int = 4
) -> List[np.ndarray]:
    """
    Genera embeddings de forma paralela para texts individuales
    
    Args:
        texts: Lista de textos
        batch_size: Tamaño de batch
        max_workers: Número de workers para paralelización
        
    Returns:
        Lista de vectores numpy
    """
    if not texts:
        return []
    
    # Para listas pequeñas, usar embed_batch directamente
    if len(texts) <= batch_size:
        embeddings_matrix = embed_batch(texts, batch_size=batch_size)
        return [embeddings_matrix[i] for i in range(len(texts))]
    
    # Para listas grandes, procesar en batches paralelos
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Dividir en batches
        batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]
        
        # Procesar batches
        future_to_batch = {
            executor.submit(embed_batch, batch, batch_size, False, False): i
            for i, batch in enumerate(batches)
        }
        
        for future in future_to_batch:
            try:
                batch_embeddings = future.result()
                results.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error en batch: {e}")
    
    return results


def cosine_similarity_vectorized(query_embedding: np.ndarray, document_embeddings: np.ndarray) -> np.ndarray:
    """
    Calcula similaridad coseno de forma vectorizada
    
    Args:
        query_embedding: Embedding de la query (embedding_dim,)
        document_embeddings: Matriz de embeddings de documentos (n_docs, embedding_dim)
        
    Returns:
        Array de similaridades (n_docs,)
    """
    # Normalizar vectores
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
    doc_norm = document_embeddings / (np.linalg.norm(document_embeddings, axis=1, keepdims=True) + 1e-8)
    
    # Calcular similaridad coseno (producto punto)
    similarities = np.dot(doc_norm, query_norm)
    
    return similarities


def compute_similarity_matrix(embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
    """
    Calcula matriz de similaridad entre dos conjuntos de embeddings
    
    Args:
        embeddings1: Primer conjunto de embeddings (n1, embedding_dim)
        embeddings2: Segundo conjunto de embeddings (n2, embedding_dim)
        
    Returns:
        Matriz de similaridad (n1, n2)
    """
    # Normalizar
    norm1 = embeddings1 / (np.linalg.norm(embeddings1, axis=1, keepdims=True) + 1e-8)
    norm2 = embeddings2 / (np.linalg.norm(embeddings2, axis=1, keepdims=True) + 1e-8)
    
    # Matriz de similaridad
    return np.dot(norm1, norm2.T)


def batch_compute_similarities(
    query_embeddings: np.ndarray, 
    document_embeddings: np.ndarray,
    batch_size: int = 100
) -> np.ndarray:
    """
    Calcula similaridades en batches para ahorrar memoria
    
    Args:
        query_embeddings: Embeddings de queries (n_queries, embedding_dim)
        document_embeddings: Embeddings de documentos (n_docs, embedding_dim)
        batch_size: Tamaño de batch para queries
        
    Returns:
        Matriz de similaridades (n_queries, n_docs)
    """
    n_queries = query_embeddings.shape[0]
    n_docs = document_embeddings.shape[0]
    
    # Normalizar todos los embeddings primero
    query_norm = query_embeddings / (np.linalg.norm(query_embeddings, axis=1, keepdims=True) + 1e-8)
    doc_norm = document_embeddings / (np.linalg.norm(document_embeddings, axis=1, keepdims=True) + 1e-8)
    
    # Calcular en batches
    similarities = np.zeros((n_queries, n_docs))
    
    for i in range(0, n_queries, batch_size):
        batch_end = min(i + batch_size, n_queries)
        batch_queries = query_norm[i:batch_end]
        
        # Similaridad del batch con todos los documentos
        similarities[i:batch_end] = np.dot(batch_queries, doc_norm.T)
    
    return similarities


def get_embedding_dimension() -> int:
    """
    Retorna la dimensión del embedding del modelo
    
    Returns:
        Dimensión del embedding
    """
    model = get_model()
    return model.get_sentence_embedding_dimension()


def preload_model():
    """
    Pre-carga el modelo de embeddings
    Útil para warmup al iniciar la aplicación
    """
    logger.info("Pre-cargando modelo de embeddings...")
    get_model()
    logger.info("Modelo pre-cargado")


def unload_model():
    """
    Descarga el modelo de la memoria
    Útil para liberar memoria cuando no se necesita
    """
    global _model, _model_name
    
    if _model is not None:
        logger.info("Descargando modelo de embeddings...")
        del _model
        _model = None
        _model_name = None
        logger.info("Modelo descargado")


# Funciones de compatibilidad con el código existente
def cosine_similarity(vec1: Union[np.ndarray, List[float]], vec2: Union[np.ndarray, List[float]]) -> float:
    """
    Calcula similaridad coseno entre dos vectores (compatibilidad)
    
    Args:
        vec1: Primer vector
        vec2: Segundo vector
        
    Returns:
        Similitud coseno (-1 a 1)
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(np.dot(vec1, vec2) / (norm1 * norm2))


def euclidean_distance(vec1: Union[np.ndarray, List[float]], vec2: Union[np.ndarray, List[float]]) -> float:
    """
    Calcula distancia euclidiana entre dos vectores (compatibilidad)
    
    Args:
        vec1: Primer vector
        vec2: Segundo vector
        
    Returns:
        Distancia euclidiana
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    return float(np.linalg.norm(vec1 - vec2))


def normalize_vector(vec: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Normaliza un vector a longitud unitaria
    
    Args:
        vec: Vector a normalizar
        
    Returns:
        Vector normalizado
    """
    vec = np.array(vec)
    norm = np.linalg.norm(vec)
    
    if norm == 0:
        return vec
    
    return vec / norm

