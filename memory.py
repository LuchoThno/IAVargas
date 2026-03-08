"""
Sistema de Memoria Persistente con Arquitectura Inteligente
==========================================================
- Memoria a corto y largo plazo
- Categorización automática
- Sistema de importancia (1-5 estrellas)
- Política de retención automática
- Embeddings para búsqueda semántica
- Migración de base de datos segura
"""

import os
import json
import re
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
import sqlite3

# Modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Configuración
DB_PATH = "data/memory.db"

# Categorías de memoria
CATEGORIES = {
    "conversation": "Conversación",
    "knowledge": "Conocimiento",
    "task": "Tarea",
    "preference": "Preferencia",
    "system": "Sistema"
}

# Scope de memoria
MEMORY_SCOPES = {
    "short": "Corto plazo",
    "long": "Largo plazo"
}

# Configuración de retención
SHORT_TERM_DAYS = 7
LONG_TERM_DAYS = 30
MAX_MEMORIES = 1000

DEFAULT_IMPORTANCE = 3


def init_db():
    """
    Inicializa la base de datos SQLite con estructura completa
    Incluye migración para esquemas antiguos
    """
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener información de la tabla existente
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        # Crear tabla nueva desde cero
        cursor.execute("""
            CREATE TABLE memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                category TEXT DEFAULT 'conversation',
                importance INTEGER DEFAULT 3,
                memory_scope TEXT DEFAULT 'short',
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                archived INTEGER DEFAULT 0
            )
        """)
        print("✓ Base de datos creada con nueva estructura")
    else:
        # Obtener columnas existentes
        cursor.execute("PRAGMA table_info(memories)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Migración: agregar columnas faltantes
        migrations = {
            "category": "ALTER TABLE memories ADD COLUMN category TEXT DEFAULT 'conversation'",
            "importance": "ALTER TABLE memories ADD COLUMN importance INTEGER DEFAULT 3",
            "memory_scope": "ALTER TABLE memories ADD COLUMN memory_scope TEXT DEFAULT 'short'",
            "created_at": "ALTER TABLE memories ADD COLUMN created_at TEXT NOT NULL DEFAULT (datetime('now'))",
            "last_accessed": "ALTER TABLE memories ADD COLUMN last_accessed TEXT NOT NULL DEFAULT (datetime('now'))",
            "access_count": "ALTER TABLE memories ADD COLUMN access_count INTEGER DEFAULT 0",
            "archived": "ALTER TABLE memories ADD COLUMN archived INTEGER DEFAULT 0"
        }
        
        for col, sql in migrations.items():
            if col not in existing_columns:
                try:
                    cursor.execute(sql)
                    print(f"✓ Migración: columna '{col}' añadida")
                except sqlite3.Error as e:
                    # La columna ya puede existir o haber otro error
                    pass
        
        # Manejar columna 'timestamp' legacy
        if "timestamp" in existing_columns and "created_at" not in existing_columns:
            try:
                cursor.execute("ALTER TABLE memories ADD COLUMN created_at TEXT NOT NULL DEFAULT (datetime('now'))")
                cursor.execute("UPDATE memories SET created_at = timestamp WHERE created_at IS NULL OR created_at = ''")
            except:
                pass
        
        if "last_accessed" not in existing_columns:
            try:
                cursor.execute("ALTER TABLE memories ADD COLUMN last_accessed TEXT NOT NULL DEFAULT (datetime('now'))")
                cursor.execute("UPDATE memories SET last_accessed = created_at WHERE last_accessed IS NULL OR last_accessed = ''")
            except:
                pass
    
    # Crear índices
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_scope ON memories(memory_scope)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_archived ON memories(archived)")
    except:
        pass
    
    conn.commit()
    conn.close()


def calculate_importance(text: str, metadata: dict = None) -> int:
    """Calcula automáticamente la importancia de una memoria"""
    text_lower = text.lower()
    
    pref_keywords = ["me gusta", "no me gusta", "prefiero", "odio", "amo", "siempre", "nunca", "mi nombre es", "soy", "tengo", "vivo en"]
    if any(kw in text_lower for kw in pref_keywords):
        return 4
    
    knowledge_keywords = ["importante", "recordar", "no olvidar", "dato", "fecha", "número", "teléfono", "email"]
    if any(kw in text_lower for kw in knowledge_keywords):
        return 4
    
    task_keywords = ["tarea", "hacer", "comprar", "llamar", "enviar", "reunión", "cita"]
    if any(kw in text_lower for kw in task_keywords):
        return 3
    
    if metadata and "importance" in metadata:
        return metadata["importance"]
    
    return 3


def determine_memory_scope(importance: int) -> str:
    """Determina el scope de memoria basado en importancia"""
    return "long" if importance >= 4 else "short"


def determine_category(text: str, metadata: dict = None) -> str:
    """Determina la categoría de la memoria"""
    text_lower = text.lower()
    
    if metadata and "category" in metadata:
        return metadata["category"]
    
    if any(kw in text_lower for kw in ["tarea", "hacer", "recordar", "comprar", "reunión"]):
        return "task"
    elif any(kw in text_lower for kw in ["me gusta", "prefiero", "no me gusta", "odio"]):
        return "preference"
    elif any(kw in text_lower for kw in ["qué es", "cómo funciona", "explica", "dato", "importante"]):
        return "knowledge"
    elif any(kw in text_lower for kw in ["sistema", "configuración", "error", "debug"]):
        return "system"
    else:
        return "conversation"


def save_memory(text: str, metadata: dict = None) -> bool:
    """Guarda un mensaje en la memoria persistente"""
    try:
        importance = calculate_importance(text, metadata)
        memory_scope = determine_memory_scope(importance)
        category = determine_category(text, metadata)
        embedding = model.encode(text).tolist()
        
        now = datetime.now().isoformat()
        
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memories (
                text, embedding, category, importance, memory_scope,
                created_at, last_accessed, access_count, archived
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (text, json.dumps(embedding), category, importance, memory_scope, 
              now, now, 0, 0))
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM memories WHERE archived = 0")
        count = cursor.fetchone()[0]
        
        if count > MAX_MEMORIES:
            delete_count = count - MAX_MEMORIES + 100
            cursor.execute("""
                DELETE FROM memories 
                WHERE id IN (
                    SELECT id FROM memories 
                    WHERE archived = 0 
                    ORDER BY importance ASC, created_at ASC 
                    LIMIT ?
                )
            """, (delete_count,))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error guardando memoria: {e}")
        return False


def search_memory(query: str, n_results: int = 5, category: str = None, 
                 min_importance: int = 1, memory_scope: str = None) -> str:
    """Busca recuerdos relevantes usando embeddings semánticos"""
    try:
        query_embedding = model.encode(query)
        
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        sql = """SELECT id, text, embedding, category, importance, memory_scope, access_count 
                 FROM memories WHERE archived = 0 AND importance >= ?"""
        params = [min_importance]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if memory_scope:
            sql += " AND memory_scope = ?"
            params.append(memory_scope)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return ""
        
        scores = []
        for row in rows:
            emb = np.array(json.loads(row[2]))
            similarity = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            importance_boost = row[4] / 5.0 * 0.2
            freq_boost = min(row[6] / 10.0, 0.1) if row[6] else 0
            total_score = similarity + importance_boost + freq_boost
            
            scores.append({
                "score": total_score,
                "text": row[1],
                "category": row[3],
                "importance": row[4],
                "scope": row[5],
                "id": row[0]
            })
        
        scores.sort(key=lambda x: x["score"], reverse=True)
        results = scores[:n_results]
        
        for result in results:
            cursor.execute("""
                UPDATE memories SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), result["id"]))
        
        conn.commit()
        conn.close()
        
        if results:
            return "\n\n".join([
                f"[{r['category']}]⭐{r['importance']}({r['scope']}): {r['text']}" 
                for r in results
            ])
        
        return ""
        
    except Exception as e:
        print(f"Error buscando memoria: {e}")
        return ""


def clean_old_memories() -> dict:
    """Limpia memorias antiguas según la política de retención"""
    try:
        now = datetime.now()
        
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        stats = {"deleted": 0, "archived": 0}
        
        # 1. Eliminar short_term mayores a 7 días
        try:
            cutoff_short = (now - timedelta(days=SHORT_TERM_DAYS)).isoformat()
            cursor.execute("""
                DELETE FROM memories 
                WHERE memory_scope = 'short' 
                AND created_at < ?
                AND (archived = 0 OR archived IS NULL)
            """, (cutoff_short,))
            stats["deleted"] = cursor.rowcount
        except Exception as e:
            print(f"Warning: Error en limpieza short-term: {e}")
        
        # 2. Archivar importance <= 2 mayores a 30 días
        try:
            cutoff_long = (now - timedelta(days=LONG_TERM_DAYS)).isoformat()
            cursor.execute("""
                UPDATE memories 
                SET archived = 1 
                WHERE importance <= 2 
                AND created_at < ?
                AND (archived = 0 OR archived IS NULL)
            """, (cutoff_long,))
            stats["archived"] = cursor.rowcount
        except Exception as e:
            print(f"Warning: Error en archivado: {e}")
        
        conn.commit()
        
        # 3. Eliminar si excede el máximo
        try:
            cursor.execute("SELECT COUNT(*) FROM memories WHERE archived = 0 OR archived IS NULL")
            count = cursor.fetchone()[0] or 0
            
            if count > MAX_MEMORIES:
                excess = count - MAX_MEMORIES
                cursor.execute("""
                    UPDATE memories 
                    SET archived = 1 
                    WHERE id IN (
                        SELECT id FROM memories 
                        WHERE archived = 0 OR archived IS NULL
                        ORDER BY importance ASC, created_at ASC 
                        LIMIT ?
                    )
                """, (excess,))
                stats["archived"] += cursor.rowcount
        except Exception as e:
            print(f"Warning: Error en límite máximo: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"🧹 Limpieza de memorias: {stats}")
        return stats
        
    except Exception as e:
        print(f"Error en limpieza: {e}")
        return {"error": str(e)}


def get_all_memories(limit: int = 20, category: str = None, memory_scope: str = None) -> list:
    """Obtiene memorias con filtros"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        sql = "SELECT id, text, category, importance, memory_scope, created_at, access_count FROM memories WHERE (archived = 0 OR archived IS NULL)"
        params = []
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if memory_scope:
            sql += " AND memory_scope = ?"
            params.append(memory_scope)
        
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [{"id": row[0], "text": row[1], "category": row[2], "importance": row[3], 
                "memory_scope": row[4], "created_at": row[5], "access_count": row[6]} for row in rows]
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_memories_by_category(category: str, limit: int = 20) -> list:
    return get_all_memories(limit=limit, category=category)


def get_long_term_memories(limit: int = 20) -> list:
    return get_all_memories(limit=limit, memory_scope="long")


def get_short_term_memories(limit: int = 20) -> list:
    return get_all_memories(limit=limit, memory_scope="short")


def get_important_memories(min_importance: int = 4, limit: int = 10) -> list:
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, text, category, importance, memory_scope, created_at
            FROM memories 
            WHERE importance >= ? AND (archived = 0 OR archived IS NULL)
            ORDER BY importance DESC, created_at DESC 
            LIMIT ?
        """, (min_importance, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{"id": r[0], "text": r[1], "category": r[2], "importance": r[3], 
                "memory_scope": r[4], "created_at": r[5]} for r in rows]
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def update_memory_importance(memory_id: int, importance: int):
    try:
        importance = min(5, max(1, importance))
        memory_scope = determine_memory_scope(importance)
        
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE memories SET importance = ?, memory_scope = ?
            WHERE id = ?
        """, (importance, memory_scope, memory_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def archive_memory(memory_id: int):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE memories SET archived = 1 WHERE id = ?", (memory_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def clear_memory():
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories")
        conn.commit()
        conn.close()
        print("✓ Memoria limpiada")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_memory_count() -> int:
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories WHERE archived = 0 OR archived IS NULL")
        count = cursor.fetchone()[0]
        conn.close()
        return count or 0
    except:
        return 0


def get_memory_stats() -> dict:
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM memories WHERE archived = 0 OR archived IS NULL")
        total = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT category, COUNT(*) FROM memories 
            WHERE archived = 0 OR archived IS NULL GROUP BY category
        """)
        by_category = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT importance, COUNT(*) FROM memories 
            WHERE archived = 0 OR archived IS NULL GROUP BY importance
        """)
        by_importance = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT memory_scope, COUNT(*) FROM memories 
            WHERE archived = 0 OR archived IS NULL GROUP BY memory_scope
        """)
        by_scope = dict(cursor.fetchall())
        
        conn.close()
        
        return {"total": total, "by_category": by_category, "by_importance": by_importance, "by_scope": by_scope}
    except Exception as e:
        return {"error": str(e)}


# Funciones de compatibilidad
def save_memory_legacy(text: str) -> bool:
    return save_memory(text, {"type": "legacy"})


def search_memory_legacy(query: str) -> str:
    return search_memory(query, n_results=3)


search = search_memory
get = get_all_memories
add = save_memory
remove = clear_memory


if __name__ == "__main__":
    print("🚀 Inicializando sistema de memoria...")
    init_db()
    print("🧹 Ejecutando limpieza automática...")
    clean_old_memories()
    print(f"📊 Estado de memoria: {get_memory_stats()}")
