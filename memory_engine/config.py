"""
Configuración del Memory Engine
================================
IA Local Vargas - Sistema de Memoria Modular
"""

import os

# Rutas
DB_PATH = "data/memory.db"
DATA_DIR = "data"
DOCUMENTS_DIR = "documents"

# Modelo de embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # Dimensión de all-MiniLM-L6-v2

# Límites
MAX_MEMORIES = 5000

# Chunking de documentos
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MIN_CHUNK_SIZE = 100
MAX_CHUNK_SIZE = 1000

# Embeddings
EMBEDDING_BATCH_SIZE = 32
EMBEDDING_MAX_WORKERS = 4

# Búsqueda semántica
SEMANTIC_MIN_SCORE = 0.3
SEMANTIC_DEFAULT_K = 5

# RAG
RAG_MAX_TOKENS = 4000
RAG_DEDUPLICATE = True
RAG_RANK_BY = "score"  # score, position, diversity

# FAISS
USE_FAISS = True
FAISS_INDEX_TYPE = "flat"  # flat, ivf, hnsw

# Documentos
DOCUMENT_CACHE_FILE = "data/document_cache.json"
DOCUMENT_EMBEDDINGS_FILE = "data/document_embeddings.json"
MAX_DOCUMENT_SIZE_MB = 50  # Máximo tamaño de documento a procesar

# Paralelización
MAX_WORKERS = 4  # Para procesamiento paralelo de documentos

# Políticas de retención
SHORT_TERM_DAYS = 7
LONG_TERM_DAYS = 30
IMPORTANCE_SCALE = 5

# Scores
WEIGHT_SIMILARITY = 0.6
WEIGHT_IMPORTANCE = 0.2
WEIGHT_RECENCY = 0.1
WEIGHT_FREQUENCY = 0.1

# Tipos de memoria
MEMORY_TYPES = {
    "episodic": "Episódica - Experiencias y eventos",
    "semantic": "Semántica - Conocimiento y hechos",
    "procedural": "Procedural - Procesos y procedimientos"
}

# Categorías legacy
CATEGORIES = {
    "conversation": "Conversación",
    "knowledge": "Conocimiento",
    "task": "Tarea",
    "preference": "Preferencia",
    "system": "Sistema"
}

