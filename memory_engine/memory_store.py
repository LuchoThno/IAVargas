"""
Memory Storage - Almacenamiento de Memorias
===========================================
IA Local Vargas - Memory Engine
Gestiona el guardado de memorias con embeddings
"""

from typing import Optional, Dict, Any
from . import db
from . import embeddings
from . import memory_router
from . import config


def save_memory(text: str, importance: int = -1, metadata: dict = None) -> Optional[int]:
    """
    Guarda una memoria en el sistema
    Args:
        text: Contenido de la memoria
        importance: Importancia (1-5), si es -1 se calcula automáticamente
        metadata: Metadatos adicionales (category, etc.)
    Returns:
        ID de la memoria guardada o None si falla
    """
    try:
        # 1. Generar embedding
        vector = embeddings.embed(text)
        
        # 2. Clasificar tipo de memoria
        memory_type = memory_router.classify_memory(text)
        
        # 3. Calcular importancia si no se especifica
        if importance == -1:
            if metadata and "importance" in metadata:
                importance = metadata["importance"]
            else:
                importance = memory_router.suggest_importance(text)
        
        # 4. Guardar en base de datos
        memory_id = db.insert_memory(
            text=text,
            memory_type=memory_type,
            importance=importance,
            vector=vector.tolist()
        )
        
        if memory_id:
            print(f"✓ Memoria guardada (ID: {memory_id}, Tipo: {memory_type}, Importancia: {importance})")
        
        return memory_id
        
    except Exception as e:
        print(f"Error guardando memoria: {e}")
        return None


def get_memory(memory_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene una memoria por su ID"""
    return db.get_memory_by_id(memory_id)


def get_memory_embedding(memory_id: int) -> Optional[list]:
    """Obtiene el embedding de una memoria"""
    return db.get_embedding_by_memory_id(memory_id)


def get_all_memories() -> list:
    """Obtiene todas las memorias"""
    return db.get_all_memories()


def get_memories_by_type(memory_type: str) -> list:
    """Obtiene memorias por tipo"""
    return db.get_memories_by_type(memory_type)


def get_episodic_memories() -> list:
    """Obtiene memorias episódicas"""
    return db.get_memories_by_type("episodic")


def get_semantic_memories() -> list:
    """Obtiene memorias semánticas"""
    return db.get_memories_by_type("semantic")


def get_procedural_memories() -> list:
    """Obtiene memorias procedimentales"""
    return db.get_memories_by_type("procedural")


def get_long_term_memories(limit: int = 20) -> list:
    """
    Obtiene memorias de largo plazo (importancia >= 4)
    """
    all_memories = db.get_all_memories()
    long_term = [m for m in all_memories if m.get("importance", 0) >= 4]
    return long_term[:limit]


def get_short_term_memories(limit: int = 20) -> list:
    """
    Obtiene memorias de corto plazo (importancia < 4)
    """
    all_memories = db.get_all_memories()
    short_term = [m for m in all_memories if m.get("importance", 0) < 4]
    return short_term[:limit]


def update_importance(memory_id: int, importance: int):
    """Actualiza la importancia de una memoria"""
    importance = max(1, min(5, importance))
    db.update_memory_importance(memory_id, importance)


def delete_memory(memory_id: int) -> bool:
    """Elimina una memoria"""
    return db.delete_memory(memory_id)


def get_memory_count() -> int:
    """Retorna el número de memorias"""
    return db.get_memory_count()


def clear_all_memories() -> bool:
    """Elimina todas las memorias"""
    return db.clear_all_memories()


# Alias de compatibilidad con app.py
def clear_memory() -> bool:
    """Alias de clear_all_memories para compatibilidad"""
    return clear_all_memories()


def get_memory_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de las memorias"""
    all_memories = db.get_all_memories()
    
    stats = {
        "total": len(all_memories),
        "by_type": {},
        "by_importance": {},
        "average_importance": 0
    }
    
    # Contar por tipo
    for memory in all_memories:
        mem_type = memory.get("memory_type", "unknown")
        stats["by_type"][mem_type] = stats["by_type"].get(mem_type, 0) + 1
        
        importance = memory.get("importance", 3)
        stats["by_importance"][importance] = stats["by_importance"].get(importance, 0) + 1
    
    # Calcular importancia promedio
    if all_memories:
        total_importance = sum(m.get("importance", 3) for m in all_memories)
        stats["average_importance"] = round(total_importance / len(all_memories), 2)
    
    return stats


def search_by_text(text: str, memory_type: str = None, min_importance: int = 1) -> list:
    """
    Busca memorias por texto exacto (no semántico)
    Args:
        text: Texto a buscar
        memory_type: Filtrar por tipo (opcional)
        min_importance: Importancia mínima
    Returns:
        Lista de memorias coincidentes
    """
    all_memories = db.get_all_memories()
    results = []
    
    text_lower = text.lower()
    
    for memory in all_memories:
        # Filtrar por tipo
        if memory_type and memory.get("memory_type") != memory_type:
            continue
        
        # Filtrar por importancia
        if memory.get("importance", 3) < min_importance:
            continue
        
        # Buscar en texto
        if text_lower in memory.get("text", "").lower():
            results.append(memory)
    
    return results

