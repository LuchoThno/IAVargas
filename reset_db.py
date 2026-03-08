#!/usr/bin/env python
"""
Script para resetear la base de datos de memoria
Úsalo si hay errores de esquema o columnas faltantes
"""

import os
import sqlite3
import time

DB_PATH = "data/memory.db"

def reset_database():
    """Elimina y recrea la base de datos"""
    
    print("🔄 Reseteando base de datos...")
    
    # Intentar eliminar el archivo
    for i in range(3):
        try:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
                print(f"✓ Eliminado: {DB_PATH}")
            break
        except PermissionError:
            print(f"⚠️ Archivo bloqueado, intento {i+1}/3...")
            time.sleep(1)
    
    # Crear nueva base de datos
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear tabla con nueva estructura
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
    
    # Crear índices
    cursor.execute("CREATE INDEX idx_created_at ON memories(created_at)")
    cursor.execute("CREATE INDEX idx_category ON memories(category)")
    cursor.execute("CREATE INDEX idx_importance ON memories(importance)")
    cursor.execute("CREATE INDEX idx_memory_scope ON memories(memory_scope)")
    cursor.execute("CREATE INDEX idx_archived ON memories(archived)")
    
    conn.commit()
    conn.close()
    
    print("✓ Base de datos recreada con nueva estructura")
    print(f"📁 Ubicación: {os.path.abspath(DB_PATH)}")

if __name__ == "__main__":
    reset_database()
