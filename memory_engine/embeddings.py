"""
Sistema de Embeddings
====================
IA Local Vargas - Memory Engine
Utiliza SentenceTransformers para generar embeddings

NOTA: Este módulo mantiene compatibilidad con código existente.
Para nuevas implementaciones, usar embedding_engine.py
"""

import logging
from typing import List, Union
import numpy as np

# Importar del motor optimizado
from . import embedding_engine

logger = logging.getLogger(__name__)

# Re-exportar funciones del motor optimizado
# El modelo se carga lazy automáticamente


def get_model():
    """Obtiene el modelo de embeddings (lazy loading)"""
    return embedding_engine.get_model()


def embed(text: str, normalize: bool = True) -> np.ndarray:
    """
    Genera un embedding para el texto dado
    Args:
        text: Texto a embeber
        normalize: Si True, normaliza el vector
    Returns:
        Vector numpy con el embedding
    """
    return embedding_engine.embed(text, normalize=normalize)


def embed_batch(
    texts: List[str], 
    batch_size: int = 32,
    normalize: bool = True,
    show_progress: bool = True
) -> np.ndarray:
    """
    Genera embeddings para una lista de textos
    Args:
        texts: Lista de textos a embeber
        batch_size: Tamaño de batch
        normalize: Normalizar vectores
        show_progress: Mostrar barra de progreso
    Returns:
        Matriz numpy con los embeddings (n_texts, embedding_dim)
    """
    return embedding_engine.embed_batch(
        texts, 
        batch_size=batch_size,
        normalize=normalize,
        show_progress=show_progress
    )


def cosine_similarity(
    vec1: Union[np.ndarray, List[float]], 
    vec2: Union[np.ndarray, List[float]]
) -> float:
    """
    Calcula la similitud coseno entre dos vectores
    Args:
        vec1: Primer vector
        vec2: Segundo vector
    Returns:
        Similitud coseno (-1 a 1)
    """
    return embedding_engine.cosine_similarity(vec1, vec2)


def euclidean_distance(
    vec1: Union[np.ndarray, List[float]], 
    vec2: Union[np.ndarray, List[float]]
) -> float:
    """
    Calcula la distancia euclidiana entre dos vectores
    Args:
        vec1: Primer vector
        vec2: Segundo vector
    Returns:
        Distancia euclidiana
    """
    return embedding_engine.euclidean_distance(vec1, vec2)


def get_embedding_dimension() -> int:
    """Retorna la dimensión del embedding del modelo"""
    return embedding_engine.get_embedding_dimension()


def normalize_vector(vec: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Normaliza un vector a longitud unitaria
    Args:
        vec: Vector a normalizar
    Returns:
        Vector normalizado
    """
    return embedding_engine.normalize_vector(vec)


def preload_model():
    """Pre-carga el modelo de embeddings"""
    embedding_engine.preload_model()


def unload_model():
    """Descarga el modelo de la memoria"""
    embedding_engine.unload_model()

