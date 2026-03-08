"""
Memory Cleanup - Limpieza Automática de Memorias
===============================================
IA Local Vargas - Memory Engine
Gestiona la eliminación y archivado de memorias antiguas
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from . import db
from . import config


def clean_old_memories() -> Dict[str, int]:
    """
    Limpia memorias antiguas según la política de retención
    - Short-term > 7 días: eliminar
    - Importancia <= 2 y > 30 días: archivar (marcar para eliminación)
    Returns:
        Diccionario con estadísticas de limpieza
    """
    stats = {
        "deleted": 0,
        "archived": 0,
        "errors": 0
    }
    
    try:
        now = datetime.now()
        
        # 1. Eliminar short-term memories mayores a SHORT_TERM_DAYS
        cutoff_short = (now - timedelta(days=config.SHORT_TERM_DAYS)).isoformat()
        
        all_memories = db.get_all_memories()
        short_term_old = [
            m for m in all_memories
            if m.get("memory_type") == "episodic" and m.get("created_at", "") < cutoff_short
        ]
        
        for memory in short_term_old:
            if db.delete_memory(memory["id"]):
                stats["deleted"] += 1
            else:
                stats["errors"] += 1
        
        # 2. Archivar importancia <= 2 mayores a LONG_TERM_DAYS
        cutoff_long = (now - timedelta(days=config.LONG_TERM_DAYS)).isoformat()
        
        low_importance_old = [
            m for m in all_memories
            if m.get("importance", 3) <= 2 and m.get("created_at", "") < cutoff_long
        ]
        
        # En lugar de eliminar, las marcamos archivadas
        # (en este implementación simple, las eliminamos directamente)
        for memory in low_importance_old:
            if db.delete_memory(memory["id"]):
                stats["archived"] += 1
            else:
                stats["errors"] += 1
        
        # 3. Verificar límite máximo de memorias
        current_count = db.get_memory_count()
        
        if current_count > config.MAX_MEMORIES:
            excess = current_count - config.MAX_MEMORIES
            
            # Obtener memorias menos importantes
            sorted_memories = sorted(
                all_memories,
                key=lambda x: (x.get("importance", 0), x.get("created_at", ""))
            )
            
            to_delete = sorted_memories[:excess]
            
            for memory in to_delete:
                if db.delete_memory(memory["id"]):
                    stats["deleted"] += 1
        
        print(f"[LIMPIEZA] Memoria limpiada: {stats}")
        
    except Exception as e:
        print(f"Error en limpieza: {e}")
        stats["errors"] = 1
    
    return stats


def get_memories_to_cleanup(days: int = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Obtiene memorias que serían limpiadas
    Args:
        days: Días de antigüedad (None = SHORT_TERM_DAYS)
    Returns:
        Diccionario con categorías de memorias a limpiar
    """
    if days is None:
        days = config.SHORT_TERM_DAYS
    
    all_memories = db.get_all_memories()
    now = datetime.now()
    cutoff = (now - timedelta(days=days)).isoformat()
    
    result = {
        "short_term_old": [],
        "low_importance_old": [],
        "excess_memories": []
    }
    
    # Short-term mayores a X días
    result["short_term_old"] = [
        m for m in all_memories
        if m.get("created_at", "") < cutoff
    ]
    
    # Importancia <= 2 mayores a LONG_TERM_DAYS
    cutoff_long = (now - timedelta(days=config.LONG_TERM_DAYS)).isoformat()
    result["low_importance_old"] = [
        m for m in all_memories
        if m.get("importance", 3) <= 2 and m.get("created_at", "") < cutoff_long
    ]
    
    # Exceso sobre MAX_MEMORIES
    if len(all_memories) > config.MAX_MEMORIES:
        sorted_memories = sorted(
            all_memories,
            key=lambda x: (x.get("importance", 0), x.get("created_at", ""))
        )
        result["excess_memories"] = sorted_memories[:len(all_memories) - config.MAX_MEMORIES]
    
    return result


def auto_cleanup():
    """Función de conveniencia para ejecutar limpieza automática"""
    return clean_old_memories()


def set_retention_policy(short_term_days: int = None, long_term_days: int = None, 
                         max_memories: int = None):
    """
    Actualiza la política de retención
    Args:
        short_term_days: Días para short-term
        long_term_days: Días para long-term
        max_memories: Máximo de memorias
    """
    if short_term_days is not None:
        config.SHORT_TERM_DAYS = short_term_days
    
    if long_term_days is not None:
        config.LONG_TERM_DAYS = long_term_days
    
    if max_memories is not None:
        config.MAX_MEMORIES = max_memories


def get_retention_policy() -> dict:
    """Retorna la política de retención actual"""
    return {
        "short_term_days": config.SHORT_TERM_DAYS,
        "long_term_days": config.LONG_TERM_DAYS,
        "max_memories": config.MAX_MEMORIES,
        "importance_scale": config.IMPORTANCE_SCALE
    }

