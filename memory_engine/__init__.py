"""
Memory Engine Package
====================
IA Local Vargas - Modular AI Memory Engine

Módulos:
- config: Configuración centralizada
- db: Capa de base de datos SQLite
- embeddings: Sistema de embeddings con SentenceTransformers (compatibilidad)
- embedding_engine: Motor de embeddings optimizado
- document_loader: Carga de documentos con procesamiento paralelo
- text_chunker: Segmentación de texto semántica
- vector_index: Índice vectorial con FAISS
- semantic_search: Búsqueda semántica vectorizada
- rag_context_builder: Constructor de contexto para RAG
- memory_router: Clasificación de tipos de memoria
- memory_store: Almacenamiento de memorias
- memory_search: Motor de búsqueda semántica
- memory_scoring: Sistema de puntuación
- memory_cleanup: Limpieza automática
- knowledge_graph: Grafo de conocimientos

Uso:
    from memory_engine import init_db, save_memory, search_memory
    
    init_db()
    save_memory("El usuario trabaja en el puerto de Talcahuano", 5)
    save_memory("Servasmar es una empresa de software marítimo", 4)
    
    results = search_memory("donde trabaja el usuario")
    print(results)
"""

from .config import (
    DB_PATH,
    DATA_DIR,
    DOCUMENTS_DIR,
    EMBEDDING_MODEL,
    EMBEDDING_DIM,
    MAX_MEMORIES,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_BATCH_SIZE,
    SEMANTIC_MIN_SCORE,
    RAG_MAX_TOKENS,
    SHORT_TERM_DAYS,
    LONG_TERM_DAYS,
    IMPORTANCE_SCALE,
    MEMORY_TYPES,
    CATEGORIES
)

from .db import init_db, get_connection

# Embeddings - usar la versión optimizada internamente
from .embeddings import embed, embed_batch, cosine_similarity

# Nuevos módulos
from .embedding_engine import (
    embed as embed_optimized,
    embed_batch as embed_batch_optimized,
    cosine_similarity_vectorized,
    compute_similarity_matrix,
    get_embedding_dimension,
    preload_model,
    unload_model
)

from .document_loader import (
    DocumentLoader,
    get_document_loader,
    load_documents_parallel,
    get_file_hash as get_file_hash_chunked
)

from .text_chunker import (
    TextChunker,
    ChunkConfig,
    chunk_text,
    chunk_for_rag
)

from .semantic_search import (
    SemanticSearch,
    get_search_engine,
    search_semantic,
    search_with_metadata
)

from .rag_context_builder import (
    RAGContextBuilder,
    get_rag_builder,
    build_rag_context,
    get_relevant_documents_for_rag
)

from .memory_router import (
    classify_memory,
    get_memory_type_info,
    get_all_memory_types,
    suggest_importance
)

from .memory_store import (
    save_memory,
    get_memory,
    get_all_memories,
    get_memories_by_type,
    get_memory_count,
    clear_all_memories,
    clear_memory,
    get_memory_stats,
    get_long_term_memories,
    get_short_term_memories,
    get_episodic_memories,
    get_semantic_memories,
    get_procedural_memories
)

from .memory_search import (
    search_memory,
    search_memory_string,
    search_by_text_match,
    get_similar_memories,
    get_recent_memories,
    get_important_memories,
    format_search_results
)

from .memory_cleanup import (
    clean_old_memories,
    get_memories_to_cleanup,
    auto_cleanup,
    get_retention_policy
)

from .knowledge_graph import (
    add_relation,
    get_outgoing_relations,
    get_incoming_relations,
    get_related_memories,
    auto_create_relations,
    get_knowledge_graph_summary,
    format_relation
)

# Versión del paquete
__version__ = "2.0.0"
__author__ = "IA Local Vargas"

# Exports principales
__all__ = [
    # Config
    "DB_PATH",
    "DATA_DIR",
    "DOCUMENTS_DIR",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIM",
    "MAX_MEMORIES",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "EMBEDDING_BATCH_SIZE",
    "SEMANTIC_MIN_SCORE",
    "RAG_MAX_TOKENS",
    # DB
    "init_db",
    "get_connection",
    # Embeddings (compatibilidad)
    "embed",
    "embed_batch", 
    "cosine_similarity",
    # Embedding Engine (nuevo)
    "embed_optimized",
    "embed_batch_optimized",
    "cosine_similarity_vectorized",
    "compute_similarity_matrix",
    "get_embedding_dimension",
    "preload_model",
    "unload_model",
    # Document Loader
    "DocumentLoader",
    "get_document_loader",
    "load_documents_parallel",
    "get_file_hash_chunked",
    # Text Chunker
    "TextChunker",
    "ChunkConfig",
    "chunk_text",
    "chunk_for_rag",
    # Semantic Search
    "SemanticSearch",
    "get_search_engine",
    "search_semantic",
    "search_with_metadata",
    # RAG Context Builder
    "RAGContextBuilder",
    "get_rag_builder",
    "build_rag_context",
    "get_relevant_documents_for_rag",
    # Router
    "classify_memory",
    "get_memory_type_info",
    "get_all_memory_types",
    "suggest_importance",
    # Store
    "save_memory",
    "get_memory",
    "get_all_memories",
    "get_memories_by_type",
    "get_memory_count",
    "clear_all_memories",
    "clear_memory",
    "get_memory_stats",
    "get_long_term_memories",
    "get_short_term_memories",
    "get_episodic_memories",
    "get_semantic_memories",
    "get_procedural_memories",
    # Search
    "search_memory",
    "search_memory_string",
    "search_by_text_match",
    "get_similar_memories",
    "get_recent_memories",
    "get_important_memories",
    "format_search_results",
    # Cleanup
    "clean_old_memories",
    "get_memories_to_cleanup",
    "auto_cleanup",
    "get_retention_policy",
    # Knowledge Graph
    "add_relation",
    "get_outgoing_relations",
    "get_incoming_relations",
    "get_related_memories",
    "auto_create_relations",
    "get_knowledge_graph_summary",
    "format_relation",
]

