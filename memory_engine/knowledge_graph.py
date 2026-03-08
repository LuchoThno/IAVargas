"""
Knowledge Graph - Grafo de Conocimientos
=======================================
IA Local Vargas - Memory Engine
Gestiona relaciones entre memorias
"""

from typing import Dict, List, Any, Optional, Tuple
from . import db
from . import memory_store


def add_relation(source_id: int, relation: str, target_id: int) -> Optional[int]:
    """
    Añade una relación entre dos memorias
    Args:
        source_id: ID de la memoria fuente
        relation: Tipo de relación (e.g., "works_at", "knows", "related_to")
        target_id: ID de la memoria objetivo
    Returns:
        ID de la relación o None si falla
    """
    # Verificar que ambas memorias existan
    source = db.get_memory_by_id(source_id)
    target = db.get_memory_by_id(target_id)
    
    if not source or not target:
        print(f"Error: Una o ambas memorias no existen")
        return None
    
    return db.add_relation(source_id, relation, target_id)


def get_outgoing_relations(memory_id: int) -> List[Dict[str, Any]]:
    """Obtiene todas las relaciones salientes de una memoria"""
    return db.get_relations_by_source(memory_id)


def get_incoming_relations(memory_id: int) -> List[Dict[str, Any]]:
    """Obtiene todas las relaciones entrantes a una memoria"""
    return db.get_relations_by_target(memory_id)


def get_all_relations(memory_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """Obtiene todas las relaciones de una memoria (entrantes y salientes)"""
    return {
        "outgoing": get_outgoing_relations(memory_id),
        "incoming": get_incoming_relations(memory_id)
    }


def get_related_memories(memory_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene las memorias relacionadas a una memoria específica
    Args:
        memory_id: ID de la memoria
    Returns:
        Lista de memorias relacionadas
    """
    relations = get_all_relations(memory_id)
    related_ids = set()
    related_memories = []
    
    # Recoger IDs de memorias relacionadas
    for rel in relations["outgoing"]:
        related_ids.add(rel["target_id"])
    
    for rel in relations["incoming"]:
        related_ids.add(rel["source_id"])
    
    # Obtener las memorias
    for rel_id in related_ids:
        memory = db.get_memory_by_id(rel_id)
        if memory:
            related_memories.append(memory)
    
    return related_memories


def find_memories_by_relation(relation: str) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Encuentra pares de memorias relacionadas por un tipo de relación
    Args:
        relation: Tipo de relación
    Returns:
        Lista de tuplas (memoria_fuente, memoria_objetivo)
    """
    all_memories = db.get_all_memories()
    results = []
    
    for memory in all_memories:
        outgoing = get_outgoing_relations(memory["id"])
        
        for rel in outgoing:
            if rel["relation"] == relation:
                target = db.get_memory_by_id(rel["target_id"])
                if target:
                    results.append((memory, target))
    
    return results


def extract_relations_from_text(text: str, source_memory_id: int) -> List[Dict[str, Any]]:
    """
    Extrae relaciones potenciales del texto de una memoria
    Args:
        text: Texto de la memoria
        source_memory_id: ID de la memoria fuente
    Returns:
        Lista de relaciones potenciales
    """
    import re
    
    potential_relations = []
    text_lower = text.lower()
    
    # Patrones comunes para extraer relaciones
    relation_patterns = [
        # Trabaja en/empresa
        (r"trabajo en (.+?)(?:\.|,|$)", "works_at"),
        (r"trabajo para (.+?)(?:\.|,|$)", "works_for"),
        (r"mi empresa es (.+?)(?:\.|,|$)", "company_is"),
        
        # Ubicación
        (r"vivo en (.+?)(?:\.|,|$)", "lives_in"),
        (r"estoy en (.+?)(?:\.|,|$)", "located_in"),
        
        # Conocimiento
        (r"sé (?:sobre |acerca de )?(.+?)(?:\.|,|$)", "knows_about"),
        (r"conozco (.+?)(?:\.|,|$)", "knows"),
        
        # Objetos/Propiedades
        (r"tengo (.+?)(?:\.|,|$)", "has"),
        (r"es (?:un |una )?(.+?)(?:\.|,|$)", "is_a"),
        
        # Actividades
        (r"estudio (.+?)(?:\.|,|$)", "studies"),
        (r"me gusta (.+?)(?:\.|,|$)", "likes"),
    ]
    
    for pattern, relation_type in relation_patterns:
        matches = re.finditer(pattern, text_lower)
        
        for match in matches:
            target_text = match.group(1).strip()
            
            # Buscar si ya existe una memoria con este texto
            existing = memory_store.search_by_text(target_text)
            
            target_id = None
            if existing:
                target_id = existing[0]["id"]
            
            potential_relations.append({
                "source_id": source_memory_id,
                "relation": relation_type,
                "target_text": target_text,
                "target_id": target_id,
                "confidence": 0.8
            })
    
    return potential_relations


def auto_create_relations(memory_id: int) -> int:
    """
    Crea automáticamente relaciones para una memoria
    Args:
        memory_id: ID de la memoria
    Returns:
        Número de relaciones creadas
    """
    memory = db.get_memory_by_id(memory_id)
    
    if not memory:
        return 0
    
    # Extraer relaciones del texto
    potential_relations = extract_relations_from_text(
        memory["text"], 
        memory_id
    )
    
    created_count = 0
    
    for rel in potential_relations:
        # Si target_id no existe, crear una nueva memoria
        if rel["target_id"] is None:
            target_id = memory_store.save_memory(
                rel["target_text"], 
                importance=2
            )
            rel["target_id"] = target_id
        
        # Crear la relación
        if rel["target_id"]:
            result = add_relation(
                rel["source_id"],
                rel["relation"],
                rel["target_id"]
            )
            if result:
                created_count += 1
    
    return created_count


def get_knowledge_graph_summary() -> Dict[str, Any]:
    """
    Obtiene un resumen del grafo de conocimientos
    Returns:
        Diccionario con estadísticas del grafo
    """
    all_memories = db.get_all_memories()
    
    summary = {
        "total_memories": len(all_memories),
        "total_relations": 0,
        "relation_types": {},
        "memories_with_relations": 0,
        "most_common_relations": []
    }
    
    memories_with_relations = set()
    relation_counts = {}
    
    for memory in all_memories:
        outgoing = get_outgoing_relations(memory["id"])
        incoming = get_incoming_relations(memory["id"])
        
        if outgoing or incoming:
            memories_with_relations += 1
            summary["total_relations"] += len(outgoing) + len(incoming)
        
        for rel in outgoing:
            rel_type = rel["relation"]
            relation_counts[rel_type] = relation_counts.get(rel_type, 0) + 1
    
    summary["memories_with_relations"] = len(memories_with_relations)
    summary["relation_types"] = relation_counts
    
    # Ordenar por las más comunes
    summary["most_common_relations"] = sorted(
        relation_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    return summary


def format_relation(source_text: str, relation: str, target_text: str) -> str:
    """
    Formatea una relación como texto legible
    Args:
        source_text: Texto de la memoria fuente
        relation: Tipo de relación
        target_text: Texto de la memoria objetivo
    Returns:
        Relación formateada
    """
    relation_labels = {
        "works_at": "trabaja en",
        "works_for": "trabaja para",
        "company_is": "su empresa es",
        "lives_in": "vive en",
        "located_in": "está ubicado en",
        "knows_about": "sabe sobre",
        "knows": "conoce",
        "has": "tiene",
        "is_a": "es",
        "studies": "estudia",
        "likes": "le gusta",
        "related_to": "relacionado con"
    }
    
    label = relation_labels.get(relation, relation)
    
    return f"{source_text} → {label} → {target_text}"


def get_path_between(memory_id_1: int, memory_id_2: int, max_depth: int = 3) -> List[List[int]]:
    """
    Encuentra paths entre dos memorias (BFS simple)
    Args:
        memory_id_1: ID de la primera memoria
        memory_id_2: ID de la segunda memoria
        max_depth: Profundidad máxima de búsqueda
    Returns:
        Lista de paths encontrados
    """
    from collections import deque
    
    if memory_id_1 == memory_id_2:
        return [[memory_id_1]]
    
    # BFS
    queue = deque([(memory_id_1, [memory_id_1])])
    visited = {memory_id_1}
    paths = []
    
    while queue and len(paths) < 10:
        current, path = queue.popleft()
        
        if len(path) > max_depth:
            continue
        
        # Explorar vecinos
        outgoing = get_outgoing_relations(current)
        
        for rel in outgoing:
            neighbor = rel["target_id"]
            
            if neighbor == memory_id_2:
                paths.append(path + [neighbor])
                continue
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return paths

