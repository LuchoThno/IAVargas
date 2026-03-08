"""
Motor de Búsqueda de Memorias
============================
IA Local Vargas - Memory Engine
Búsqueda semántica usando embeddings
"""

from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
from . import db
from . import embeddings
from . import memory_scoring
from . import config


def search_memory(query: str, n_results: int = 5, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Busca memorias relevantes usando búsqueda semántica
    Args:
        query: Consulta de búsqueda
        n_results: Número de resultados a retornar
        memory_type: Filtrar por tipo de memoria (opcional)
    Returns:
        Lista de memorias con scores
    """
    try:
        # 1. Crear embedding de la consulta
        query_embedding = embeddings.embed(query)
        
        # 2. Obtener todas las memorias (o filtrar por tipo)
        if memory_type:
            all_memories = db.get_memories_by_type(memory_type)
        else:
            all_memories = db.get_all_memories()
        
        if not all_memories:
            return []
        
        # 3. Obtener todos los embeddings
        all_embeddings = db.get_all_embeddings()
        
        # Crear diccionario de embeddings por memory_id
        embeddings_dict = {emb[0]: emb[1] for emb in all_embeddings}
        
        # 4. Calcular similitud y scores
        results = []
        
        for memory in all_memories:
            memory_id = memory.get("id")
            
            # Obtener embedding de esta memoria
            if memory_id not in embeddings_dict:
                continue
            
            memory_embedding = np.array(embeddings_dict[memory_id])
            
            # Calcular similitud coseno
            similarity = embeddings.cosine_similarity(query_embedding, memory_embedding)
            
            # Calcular score completo (incluye importancia, recencia, frecuencia)
            total_score = memory_scoring.calculate_score(
                similarity=similarity,
                importance=memory.get("importance", 3),
                created_at=memory.get("created_at"),
                access_count=memory.get("access_count", 0)
            )
            
            results.append({
                "id": memory_id,
                "text": memory.get("text"),
                "memory_type": memory.get("memory_type"),
                "importance": memory.get("importance"),
                "created_at": memory.get("created_at"),
                "access_count": memory.get("access_count"),
                "similarity": round(similarity, 4),
                "total_score": round(total_score, 4)
            })
        
        # 5. Ordenar por score total
        results.sort(key=lambda x: x["total_score"], reverse=True)
        
        # 6. Actualizar contadores de acceso
        top_results = results[:n_results]
        for result in top_results:
            db.update_memory_access(result["id"])
        
        return top_results
        
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return []


def search_by_text_match(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Busca memorias por coincidencia exacta de texto
    Args:
        query: Texto a buscar
        n_results: Número de resultados
    Returns:
        Lista de memorias coincidentes
    """
    all_memories = db.get_all_memories()
    query_lower = query.lower()
    
    results = []
    for memory in all_memories:
        text_lower = memory.get("text", "").lower()
        
        # Buscar coincidencia o coincidencia exacta
        if query_lower in text_lower:
            results.append({
                "id": memory.get("id"),
                "text": memory.get("text"),
                "memory_type": memory.get("memory_type"),
                "importance": memory.get("importance"),
                "match_type": "exact" if text_lower == query_lower else "partial"
            })
    
    return results[:n_results]


def get_similar_memories(memory_id: int, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Encuentra memorias similares a una memoria específica
    Args:
        memory_id: ID de la memoria de referencia
        n_results: Número de resultados similares
    Returns:
        Lista de memorias similares
    """
    # Obtener embedding de la memoria
    memory_embedding = db.get_embedding_by_memory_id(memory_id)
    
    if not memory_embedding:
        return []
    
    # Buscar usando el texto de la memoria como query
    memory = db.get_memory_by_id(memory_id)
    if not memory:
        return []
    
    return search_memory(memory["text"], n_results=n_results)


def get_recent_memories(n_results: int = 10) -> List[Dict[str, Any]]:
    """Obtiene las memorias más recientes"""
    all_memories = db.get_all_memories()
    
    # Ordenar por fecha de creación
    sorted_memories = sorted(
        all_memories,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    
    return sorted_memories[:n_results]


def get_important_memories(min_importance: int = 4, n_results: int = 10) -> List[Dict[str, Any]]:
    """Obtiene las memorias más importantes"""
    all_memories = db.get_all_memories()
    
    # Filtrar por importancia
    important = [m for m in all_memories if m.get("importance", 3) >= min_importance]
    
    # Ordenar por importancia y luego por fecha
    sorted_memories = sorted(
        important,
        key=lambda x: (x.get("importance", 0), x.get("created_at", "")),
        reverse=True
    )
    
    return sorted_memories[:n_results]


def get_frequently_accessed(n_results: int = 10) -> List[Dict[str, Any]]:
    """Obtiene las memorias más accedidas"""
    all_memories = db.get_all_memories()
    
    # Ordenar por cantidad de accesos
    sorted_memories = sorted(
        all_memories,
        key=lambda x: x.get("access_count", 0),
        reverse=True
    )
    
    return sorted_memories[:n_results]


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Formatea los resultados de búsqueda para display
    Args:
        results: Lista de resultados
    Returns:
        String formateado
    """
    if not results:
        return "No se encontraron memorias relevantes."
    
    output = []
    output.append(f"📊 Se encontraron {len(results)} resultado(s):\n")
    
    for i, result in enumerate(results, 1):
        # Indicador de tipo
        type_emoji = {
            "episodic": "📍",
            "semantic": "📚",
            "procedural": "⚙️"
        }.get(result.get("memory_type", ""), "📝")
        
        output.append(
            f"{i}. {type_emoji} [{result.get('memory_type', 'unknown')}] "
            f"⭐{result.get('importance', 3)} "
            f"(score: {result.get('total_score', 0):.2f})"
        )
        output.append(f"   {result.get('text', '')}")
        output.append("")
    
    return "\n".join(output)


def search_memory_string(query: str, n_results: int = 5, memory_type: Optional[str] = None) -> str:
    """
    Busca memorias y retorna un string formateado para usar en prompts
    Args:
        query: Consulta de búsqueda
        n_results: Número de resultados
        memory_type: Filtrar por tipo (opcional)
    Returns:
        String con las memorias encontradas
    """
    results = search_memory(query, n_results=n_results, memory_type=memory_type)
    
    if not results:
        return ""
    
    # Formatear como el sistema legacy
    formatted = []
    for r in results:
        mem_type = r.get("memory_type", "unknown")
        importance = r.get("importance", 3)
        scope = "long" if importance >= 4 else "short"
        formatted.append(
            f"[{mem_type}]⭐{importance}({scope}): {r.get('text', '')}"
        )
    
    return "\n\n".join(formatted)

