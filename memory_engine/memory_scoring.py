"""
Sistema de Puntuación de Memorias
================================
IA Local Vargas - Memory Engine
Calcula scores basados en similitud, importancia, recencia y frecuencia
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Union, List
from . import config


def calculate_score(
    similarity: float,
    importance: int,
    created_at: Union[str, datetime],
    access_count: int
) -> float:
    """
    Calcula el score total de una memoria
    Fórmula: 0.6 * similarity + 0.2 * importance + 0.1 * recency + 0.1 * frequency
    
    Args:
        similarity: Similitud coseno (-1 a 1)
        importance: Importancia (1-5)
        created_at: Fecha de creación
        access_count: Número de accesos
    Returns:
        Score total (0 a 1)
    """
    # Normalizar similitud de [-1, 1] a [0, 1]
    normalized_similarity = (similarity + 1) / 2
    
    # Normalizar importancia de [1, 5] a [0, 1]
    normalized_importance = (importance - 1) / 4
    
    # Calcular recencia (más reciente = mayor score)
    recency_score = calculate_recency(created_at)
    
    # Normalizar frecuencia
    frequency_score = calculate_frequency(access_count)
    
    # Aplicar pesos
    total_score = (
        config.WEIGHT_SIMILARITY * normalized_similarity +
        config.WEIGHT_IMPORTANCE * normalized_importance +
        config.WEIGHT_RECENCY * recency_score +
        config.WEIGHT_FREQUENCY * frequency_score
    )
    
    return max(0, min(1, total_score))  # Clampear a [0, 1]


def calculate_recency(created_at: Union[str, datetime], decay_factor: float = 0.1) -> float:
    """
    Calcula score de recencia basado en antigüedad
    Args:
        created_at: Fecha de creación
        decay_factor: Factor de decaimiento
    Returns:
        Score de recencia (0 a 1)
    """
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at)
        except:
            return 0.5  # Valor por defecto si no se puede parsear
    
    now = datetime.now()
    age_days = (now - created_at).days
    
    # Decay exponencial
    recency = np.exp(-decay_factor * age_days)
    
    return max(0, min(1, recency))


def calculate_frequency(access_count: int, max_count: int = 20) -> float:
    """
    Calcula score de frecuencia
    Args:
        access_count: Número de accesos
        max_count: Máximo para saturación
    Returns:
        Score de frecuencia (0 a 1)
    """
    return min(access_count / max_count, 1.0)


def calculate_boost(importance: int, base_score: float, boost_factor: float = 0.1) -> float:
    """
    Calcula un boost basado en importancia
    Args:
        importance: Importancia (1-5)
        base_score: Score base
        boost_factor: Factor de boost
    Returns:
        Score con boost
    """
    if importance >= 4:
        return base_score + boost_factor
    elif importance >= 3:
        return base_score + (boost_factor / 2)
    else:
        return base_score


def rank_memories(memories: List[dict], query_embedding: np.ndarray = None) -> List[dict]:
    """
    Ordena una lista de memorias por score
    Args:
        memories: Lista de memorias
        query_embedding: Embedding de consulta (opcional)
    Returns:
        Lista ordenada de memorias
    """
    def score_memory(memory):
        return memory.get("total_score", 0)
    
    return sorted(memories, key=score_memory, reverse=True)


def get_weighted_importance(importance: int, weight: float = None) -> float:
    """
    Obtiene la importancia normalizada
    Args:
        importance: Importancia (1-5)
        weight: Peso personalizado (opcional)
    Returns:
        Importancia normalizada (0 a 1)
    """
    if weight is None:
        weight = config.WEIGHT_IMPORTANCE
    
    normalized = (importance - 1) / 4
    return normalized * weight


def explain_score(score_breakdown: dict) -> str:
    """
    Explica cómo se calculó un score
    Args:
        score_breakdown: Desglose del score
    Returns:
        Explicación en texto
    """
    output = []
    output.append("📊 Desglose del Score:")
    output.append(f"  - Similitud (60%): {score_breakdown.get('similarity', 0):.4f}")
    output.append(f"  - Importancia (20%): {score_breakdown.get('importance', 0):.4f}")
    output.append(f"  - Recencia (10%): {score_breakdown.get('recency', 0):.4f}")
    output.append(f"  - Frecuencia (10%): {score_breakdown.get('frequency', 0):.4f}")
    output.append(f"  - TOTAL: {score_breakdown.get('total', 0):.4f}")
    
    return "\n".join(output)


def calculate_detailed_score(
    similarity: float,
    importance: int,
    created_at: Union[str, datetime],
    access_count: int
) -> dict:
    """
    Calcula score con detalle de cada componente
    Returns:
        Diccionario con score total y componentes
    """
    normalized_similarity = (similarity + 1) / 2
    normalized_importance = (importance - 1) / 4
    recency = calculate_recency(created_at)
    frequency = calculate_frequency(access_count)
    
    total = (
        config.WEIGHT_SIMILARITY * normalized_similarity +
        config.WEIGHT_IMPORTANCE * normalized_importance +
        config.WEIGHT_RECENCY * recency +
        config.WEIGHT_FREQUENCY * frequency
    )
    
    return {
        "similarity": normalized_similarity,
        "importance": normalized_importance,
        "recency": recency,
        "frequency": frequency,
        "total": max(0, min(1, total))
    }

