"""
Sistema de Gestión de Documentos con búsqueda semántica y RAG
Maneja PDFs, CSVs y Excel con procesamiento optimizado
================================================================
Versión mejorada con:
- Carga lazy del modelo
- Hashing por bloques para archivos grandes
- Chunking semántico
- Embeddings en batch
- Búsqueda vectorizada
- Sistema de caché mejorado
- Logging
"""

import os
import json
import logging
import hashlib
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importar módulos del memory_engine
from memory_engine import config
from memory_engine.document_loader import DocumentLoader, get_document_loader, get_file_hash
from memory_engine.text_chunker import TextChunker, ChunkConfig, chunk_text, chunk_for_rag
from memory_engine.embedding_engine import (
    get_model, embed, embed_batch, 
    cosine_similarity_vectorized, compute_similarity_matrix
)
from memory_engine.semantic_search import SemanticSearch, search_semantic
from memory_engine.rag_context_builder import RAGContextBuilder, build_rag_context

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas
DOC_FOLDER = config.DOCUMENTS_DIR
CACHE_FILE = config.DOCUMENT_CACHE_FILE
EMBEDDINGS_FILE = config.DOCUMENT_EMBEDDINGS_FILE

# Configuración
CHUNK_SIZE = config.CHUNK_SIZE
CHUNK_OVERLAP = config.CHUNK_OVERLAP
EMBEDDING_BATCH_SIZE = config.EMBEDDING_BATCH_SIZE


# ============================================
# SISTEMA DE CACHÉ MEJORADO
# ============================================

def get_cache() -> dict:
    """Carga el caché de documentos"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Error cargando caché: {e}")
        return {}


def save_cache(cache: dict):
    """Guarda el caché de documentos"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando caché: {e}")


def validate_cache_entry(filename: str, cache_entry: dict, filepath: str) -> bool:
    """
    Valida que una entrada del caché sea válida
    
    Args:
        filename: Nombre del archivo
        cache_entry: Entrada del caché
        filepath: Ruta del archivo
        
    Returns:
        True si el caché es válido
    """
    if not cache_entry:
        return False
    
    # Verificar hash
    current_hash = get_file_hash(filepath)
    stored_hash = cache_entry.get("hash")
    
    if current_hash != stored_hash:
        logger.info(f"Hash diferente para {filename}, requiere reprocesamiento")
        return False
    
    # Verificar que el texto exista
    if not cache_entry.get("text"):
        return False
    
    return True


# ============================================
# PROCESAMIENTO DE DOCUMENTOS
# ============================================

def process_document(path: str, loader: Optional[DocumentLoader] = None) -> Optional[Dict]:
    """
    Procesa un documento según su extensión
    
    Args:
        path: Ruta al documento
        loader: Instancia de DocumentLoader (opcional)
        
    Returns:
        Diccionario con información del documento o None si hay error
    """
    if loader is None:
        loader = get_document_loader()
    
    return loader.process_document(path)


def process_documents_parallel(folder: str = DOC_FOLDER, max_workers: int = 4) -> List[Dict]:
    """
    Procesa múltiples documentos en paralelo
    
    Args:
        folder: Carpeta con documentos
        max_workers: Número de workers
        
    Returns:
        Lista de documentos procesados
    """
    loader = get_document_loader()
    return loader.load_documents_parallel(folder)


# ============================================
# LECTURA DE DOCUMENTOS CON CACHÉ
# ============================================

def read_documents(use_cache: bool = True, force_rebuild: bool = False) -> str:
    """
    Lee todos los documentos de la carpeta documents/
    Usa caché para evitar reprocesar archivos no modificados
    
    Args:
        use_cache: Si True, usa caché existente
        force_rebuild: Si True, ignora el caché y reprocesa todo
        
    Returns:
        String con todo el texto de los documentos
    """
    # Verificar que existe la carpeta
    if not os.path.exists(DOC_FOLDER):
        logger.warning(f"Carpeta '{DOC_FOLDER}' no existe")
        return ""
    
    # Obtener caché
    cache = get_cache() if use_cache else {}
    
    # Obtener lista de archivos
    files = []
    for file in os.listdir(DOC_FOLDER):
        path = os.path.join(DOC_FOLDER, file)
        if os.path.isfile(path):
            files.append((file, path))
    
    if not files:
        logger.info("No hay documentos para procesar")
        return ""
    
    logger.info(f"Procesando {len(files)} documento(s)...")
    
    all_text = []
    processed_count = 0
    
    # Procesar documentos
    loader = get_document_loader()
    
    for filename, filepath in files:
        # Verificar si necesita reprocesar
        if use_cache and not force_rebuild:
            if filename in cache:
                if validate_cache_entry(filename, cache[filename], filepath):
                    logger.info(f"✓ {filename} (desde caché)")
                    all_text.append(cache[filename]["text"])
                    continue
        
        # Procesar archivo
        logger.info(f"→ Procesando: {filename}")
        doc = process_document(filepath, loader)
        
        if doc and doc.get("text"):
            # Actualizar caché
            cache[filename] = {
                "hash": doc["hash"],
                "text": doc["text"],
                "processed": doc["processed"],
                "size": doc["size"]
            }
            all_text.append(doc["text"])
            processed_count += 1
    
    # Guardar caché actualizado
    if processed_count > 0:
        save_cache(cache)
        logger.info(f"✓ {processed_count} documento(s) procesado(s) y guardado(s) en caché")
    
    return "\n\n".join(all_text)


def get_document_info() -> List[Dict]:
    """Retorna información de los documentos disponibles"""
    if not os.path.exists(DOC_FOLDER):
        return []
    
    cache = get_cache()
    info = []
    
    for file in os.listdir(DOC_FOLDER):
        path = os.path.join(DOC_FOLDER, file)
        if os.path.isfile(path):
            file_hash = get_file_hash(path)
            cached = cache.get(file, {})
            
            info.append({
                "name": file,
                "size": os.path.getsize(path),
                "cached": cached.get("hash") == file_hash if file in cache else False,
                "processed": cached.get("processed", "Nunca")
            })
    
    return info


def rebuild_cache():
    """Fuerza el reprocesamiento de todos los documentos"""
    logger.info("Rebuilding document cache...")
    return read_documents(use_cache=False, force_rebuild=True)


# ============================================
# CHUNKING DE TEXTO
# ============================================

def get_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Divide el texto en chunks semánticos
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño de chunk
        overlap: Overlap entre chunks
        
    Returns:
        Lista de chunks
    """
    return chunk_text(text, chunk_size=chunk_size, overlap=overlap)


def get_chunks_with_metadata(text: str, chunk_size: int = CHUNK_SIZE) -> List[Dict]:
    """
    Divide el texto en chunks con metadatos
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño de chunk
        
    Returns:
        Lista de diccionarios con chunks y metadatos
    """
    return chunk_for_rag(text, chunk_size=chunk_size)


# ============================================
# EMBEDDINGS DE DOCUMENTOS
# ============================================

def get_embeddings_cache() -> dict:
    """Carga el caché de embeddings de documentos"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Error cargando caché de embeddings: {e}")
        return {}


def save_embeddings_cache(embeddings: dict):
    """Guarda el caché de embeddings de documentos"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(EMBEDDINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(embeddings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando caché de embeddings: {e}")


def build_document_embeddings(force_rebuild: bool = False) -> dict:
    """
    Construye embeddings para todos los documentos
    
    Args:
        force_rebuild: Si True, regenera todos los embeddings
        
    Returns:
        Diccionario con embeddings por documento
    """
    cache = get_cache()
    embeddings_cache = get_embeddings_cache() if not force_rebuild else {}
    
    if not cache:
        logger.warning("No hay documentos en caché para generar embeddings")
        return {}
    
    logger.info("Generando embeddings de documentos...")
    
    modified = False
    skipped = 0
    generated = 0
    
    for filename, doc_data in cache.items():
        doc_hash = doc_data.get("hash")
        
        # Verificar si necesita regenerar
        if not force_rebuild and filename in embeddings_cache:
            stored_hash = embeddings_cache[filename].get("hash")
            if stored_hash == doc_hash:
                logger.info(f"✓ {filename} (embeddings desde caché)")
                skipped += 1
                continue
        
        logger.info(f"→ Generando embeddings para: {filename}")
        text = doc_data.get("text", "")
        
        if not text:
            continue
        
        # Dividir en chunks
        chunks = get_chunks(text)
        
        if not chunks:
            continue
        
        # Generar embeddings en batch
        try:
            chunk_embeddings = embed_batch(chunks, batch_size=EMBEDDING_BATCH_SIZE)
            
            embeddings_cache[filename] = {
                "hash": doc_hash,
                "chunks": chunks,
                "embeddings": chunk_embeddings.tolist(),
                "processed": datetime.now().isoformat()
            }
            modified = True
            generated += 1
        except Exception as e:
            logger.error(f"Error generando embeddings para {filename}: {e}")
    
    if modified:
        save_embeddings_cache(embeddings_cache)
        logger.info(f"✓ {generated} embedding(s) generado(s), {skipped} desde caché")
    elif skipped > 0:
        logger.info(f"✓ {skipped} embedding(s) desde caché (sin cambios)")
    
    return embeddings_cache


# ============================================
# BÚSQUEDA SEMÁNTICA
# ============================================

def search_documents_semantic(
    query: str, 
    n_results: int = 3, 
    min_score: float = 0.3
) -> List[Dict]:
    """
    Búsqueda semántica en documentos usando embeddings
    
    Args:
        query: Consulta del usuario
        n_results: Número de resultados a retornar
        min_score: Score mínimo de similaridad (0-1)
        
    Returns:
        Lista de resultados con texto, score y fuente
    """
    try:
        # Asegurar que existan los embeddings
        embeddings = build_document_embeddings()
        
        if not embeddings:
            return []
        
        # Generar embedding de la query
        query_embedding = embed(query)
        
        results = []
        
        for filename, doc_data in embeddings.items():
            chunks = doc_data.get("chunks", [])
            chunk_embeddings = doc_data.get("embeddings", [])
            
            if not chunks or not chunk_embeddings:
                continue
            
            # Convertir a numpy array
            chunk_emb_array = np.array(chunk_embeddings)
            
            # Calcular similaridades de forma vectorizada
            similarities = cosine_similarity_vectorized(query_embedding, chunk_emb_array)
            
            # Procesar resultados
            for i, (chunk, sim) in enumerate(zip(chunks, similarities)):
                if sim >= min_score:
                    results.append({
                        "text": chunk,
                        "score": float(sim),
                        "source": filename,
                        "chunk_id": i,
                        "metadata": {"source": filename, "chunk_id": i}
                    })
        
        # Ordenar por score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tomar los mejores resultados
        return results[:n_results]
        
    except Exception as e:
        logger.error(f"Error en búsqueda semántica: {e}")
        return []


# ============================================
# RAG - CONTEXTO PARA LLM
# ============================================

def get_relevant_documents(
    query: str, 
    max_chars: int = 5000, 
    n_results: int = 3
) -> str:
    """
    Obtiene documentos relevantes para una query (para RAG)
    
    Args:
        query: Consulta del usuario
        max_chars: Máximo de caracteres a retornar
        n_results: Número de chunks a incluir
        
    Returns:
        String con el contexto de los documentos relevantes
    """
    results = search_documents_semantic(query, n_results=n_results, min_score=0.2)
    
    if not results:
        return ""
    
    # Usar el builder de contexto
    builder = RAGContextBuilder(max_tokens=max_chars // 4)
    return builder.build_context(results, query, max_chars=max_chars)


def get_relevant_documents_with_sources(
    query: str,
    max_chars: int = 5000,
    n_results: int = 3
) -> Tuple[str, Dict]:
    """
    Obtiene documentos relevantes e información de fuentes
    
    Args:
        query: Consulta
        max_chars: Caracteres máximos
        n_results: Resultados
        
    Returns:
        Tupla (contexto, info_fuentes)
    """
    results = search_documents_semantic(query, n_results=n_results, min_score=0.2)
    
    if not results:
        return "", {}
    
    builder = RAGContextBuilder(max_tokens=max_chars // 4)
    return builder.build_context_with_sources(results, query)


# ============================================
# COMPATIBILIDAD LEGACY
# ============================================

def read_documents_legacy():
    """Versión legacy para compatibilidad"""
    return read_documents()


# Funciones de compatibilidad para uso directo
def get_file_hash_legacy(filepath: str) -> str:
    """Función legacy para hash (compatibilidad)"""
    return get_file_hash(filepath)


def extract_text_from_pdf(path: str) -> str:
    """Extrae texto de PDF"""
    loader = get_document_loader()
    text, _ = loader.extract_text_from_pdf(path)
    return text


def extract_text_from_csv(path: str) -> str:
    """Extrae texto de CSV"""
    loader = get_document_loader()
    text, _ = loader.extract_text_from_csv(path)
    return text


def extract_text_from_xlsx(path: str) -> str:
    """Extrae texto de Excel"""
    loader = get_document_loader()
    text, _ = loader.extract_text_from_xlsx(path)
    return text


def extract_text_from_txt(path: str) -> str:
    """Extrae texto de TXT"""
    loader = get_document_loader()
    text, _ = loader.extract_text_from_txt(path)
    return text

