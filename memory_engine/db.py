"""
Capa de Base de Datos
=====================
IA Local Vargas - Memory Engine
Manejo de SQLite para memorias, embeddings y relaciones
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from . import config


def init_db():
    """
    Inicializa la base de datos SQLite con todas las tablas necesarias
    """
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de memorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            memory_type TEXT DEFAULT 'episodic',
            importance INTEGER DEFAULT 3,
            created_at TEXT NOT NULL,
            last_access TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        )
    """)
    
    # Tabla de embeddings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id INTEGER NOT NULL,
            vector TEXT NOT NULL,
            FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
        )
    """)
    
    # Tabla de relaciones (Knowledge Graph)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            relation TEXT NOT NULL,
            target_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES memories(id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES memories(id) ON DELETE CASCADE
        )
    """)
    
    # Índices para optimizar búsquedas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_memory ON embeddings(memory_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id)")
    
    conn.commit()
    conn.close()


def get_connection():
    """Obtiene una conexión a la base de datos"""
    return sqlite3.connect(config.DB_PATH)


def insert_memory(text: str, memory_type: str, importance: int, vector: List[float]) -> Optional[int]:
    """
    Inserta una memoria con su embedding
    Returns: memory_id o None si falla
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO memories (text, memory_type, importance, created_at, last_access, access_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (text, memory_type, importance, now, now, 0))
        
        memory_id = cursor.lastrowid
        
        # Insertar embedding
        cursor.execute("""
            INSERT INTO embeddings (memory_id, vector)
            VALUES (?, ?)
        """, (memory_id, json.dumps(vector)))
        
        conn.commit()
        conn.close()
        return memory_id
        
    except Exception as e:
        conn.close()
        print(f"Error insertando memoria: {e}")
        return None


def get_memory_by_id(memory_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene una memoria por su ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, text, memory_type, importance, created_at, last_access, access_count
            FROM memories WHERE id = ?
        """, (memory_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "text": row[1],
                "memory_type": row[2],
                "importance": row[3],
                "created_at": row[4],
                "last_access": row[5],
                "access_count": row[6]
            }
        return None
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo memoria: {e}")
        return None


def get_all_memories(include_archived: bool = False) -> List[Dict[str, Any]]:
    """Obtiene todas las memorias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, text, memory_type, importance, created_at, last_access, access_count
            FROM memories ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "text": row[1],
                "memory_type": row[2],
                "importance": row[3],
                "created_at": row[4],
                "last_access": row[5],
                "access_count": row[6]
            }
            for row in rows
        ]
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo memorias: {e}")
        return []


def get_memories_by_type(memory_type: str) -> List[Dict[str, Any]]:
    """Obtiene memorias por tipo"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, text, memory_type, importance, created_at, last_access, access_count
            FROM memories WHERE memory_type = ? ORDER BY created_at DESC
        """, (memory_type,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "text": row[1],
                "memory_type": row[2],
                "importance": row[3],
                "created_at": row[4],
                "last_access": row[5],
                "access_count": row[6]
            }
            for row in rows
        ]
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo memorias por tipo: {e}")
        return []


def get_all_embeddings() -> List[Tuple[int, List[float]]]:
    """Obtiene todos los embeddings con sus IDs de memoria"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT memory_id, vector FROM embeddings")
        rows = cursor.fetchall()
        conn.close()
        
        return [(row[0], json.loads(row[1])) for row in rows]
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo embeddings: {e}")
        return []


def get_embedding_by_memory_id(memory_id: int) -> Optional[List[float]]:
    """Obtiene el embedding de una memoria específica"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT vector FROM embeddings WHERE memory_id = ?", (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo embedding: {e}")
        return None


def update_memory_access(memory_id: int):
    """Actualiza el acceso de una memoria"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE memories 
            SET access_count = access_count + 1, last_access = ?
            WHERE id = ?
        """, (now, memory_id))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        conn.close()
        print(f"Error actualizando acceso: {e}")


def update_memory_importance(memory_id: int, importance: int):
    """Actualiza la importancia de una memoria"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE memories SET importance = ? WHERE id = ?", (importance, memory_id))
        conn.commit()
        conn.close()
        
    except Exception as e:
        conn.close()
        print(f"Error actualizando importancia: {e}")


def delete_memory(memory_id: int) -> bool:
    """Elimina una memoria y su embedding"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        conn.close()
        print(f"Error eliminando memoria: {e}")
        return False


def add_relation(source_id: int, relation: str, target_id: int) -> Optional[int]:
    """Añade una relación entre dos memorias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO relations (source_id, relation, target_id, created_at)
            VALUES (?, ?, ?, ?)
        """, (source_id, relation, target_id, now))
        
        relation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return relation_id
        
    except Exception as e:
        conn.close()
        print(f"Error añadiendo relación: {e}")
        return None


def get_relations_by_source(source_id: int) -> List[Dict[str, Any]]:
    """Obtiene todas las relaciones desde una memoria"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.id, r.source_id, r.relation, r.target_id, r.created_at, m.text
            FROM relations r
            JOIN memories m ON r.target_id = m.id
            WHERE r.source_id = ?
        """, (source_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "source_id": row[1],
                "relation": row[2],
                "target_id": row[3],
                "created_at": row[4],
                "target_text": row[5]
            }
            for row in rows
        ]
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo relaciones: {e}")
        return []


def get_relations_by_target(target_id: int) -> List[Dict[str, Any]]:
    """Obtiene todas las relaciones hacia una memoria"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.id, r.source_id, r.relation, r.target_id, r.created_at, m.text
            FROM relations r
            JOIN memories m ON r.source_id = m.id
            WHERE r.target_id = ?
        """, (target_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "source_id": row[1],
                "relation": row[2],
                "target_id": row[3],
                "created_at": row[4],
                "source_text": row[5]
            }
            for row in rows
        ]
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo relaciones: {e}")
        return []


def get_memory_count() -> int:
    """Retorna el número total de memorias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        conn.close()
        return count
        
    except Exception as e:
        conn.close()
        return 0


def get_memories_older_than(days: int) -> List[Dict[str, Any]]:
    """Obtiene memorias mayores a X días"""
    from datetime import timedelta
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute("""
            SELECT id, text, memory_type, importance, created_at, last_access, access_count
            FROM memories WHERE created_at < ?
        """, (cutoff,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "text": row[1],
                "memory_type": row[2],
                "importance": row[3],
                "created_at": row[4],
                "last_access": row[5],
                "access_count": row[6]
            }
            for row in rows
        ]
        
    except Exception as e:
        conn.close()
        print(f"Error obteniendo memorias antiguas: {e}")
        return []


def clear_all_memories() -> bool:
    """Elimina todas las memorias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM memories")
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        conn.close()
        print(f"Error limpiando memorias: {e}")
        return False

