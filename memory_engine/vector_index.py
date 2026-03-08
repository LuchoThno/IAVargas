"""
Vector Index - Índice Vectorial con FAISS
========================================
IA Local Vargas - Memory Engine
Sistema de búsqueda vectorial eficiente usando FAISS

Mejoras implementadas:
- IndexIDMap para manejo directo de IDs en FAISS
- Fallback real con NumPy
- Compresión de embeddings (float16)
- Optimización automática HNSW para >10k vectores
- Búsqueda híbrida (vector + keyword)
- Función para formatear contexto RAG
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Intentar importar FAISS
FAISS_AVAILABLE = False
faiss = None

try:
    import faiss
    FAISS_AVAILABLE = True
    logger.info("FAISS disponible para búsqueda vectorial")
except ImportError:
    logger.warning("FAISS no disponible. Usando fallback numpy.")


@dataclass
class IndexMetadata:
    """Metadatos del índice"""
    index_type: str = "flat"
    embedding_dim: int = 384
    num_vectors: int = 0
    created_at: str = ""
    last_updated: str = ""
    model_name: str = ""
    description: str = ""


class VectorIndex:
    """
    Clase para gestionar índice vectorial con FAISS
    
    Mejoras:
    - IndexIDMap para indexing directo de IDs
    - Fallback real con NumPy cuando FAISS no está disponible
    - Compresión de embeddings a float16 para ahorrar RAM
    - Cambio automático a HNSW para grandes volúmenes (>10k)
    - Búsqueda híbrida con palabras clave
    """
    
    # Constantes para optimización
    HNSW_THRESHOLD = 10000  # Cambiar a HNSW si hay más de 10k vectores
    HNSW_THRESHOLD_IVF = 50000  # Cambiar a IVF si hay más de 50k vectores
    
    def __init__(
        self, 
        embedding_dim: int = 384,
        index_type: str = "flat",
        index_path: Optional[str] = None,
        metadata_path: Optional[str] = None,
        auto_optimize: bool = True
    ):
        """
        Inicializa el índice vectorial
        
        Args:
            embedding_dim: Dimensión de los embeddings
            index_type: Tipo de índice ('flat', 'ivf', 'hnsw')
            index_path: Ruta para guardar el índice
            metadata_path: Ruta para guardar metadatos
            auto_optimize: Si True, cambia automáticamente a HNSW para >10k vectores
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.index_path = index_path or "data/vector_index.faiss"
        self.metadata_path = metadata_path or "data/vector_index_meta.json"
        self.auto_optimize = auto_optimize
        
        self.index = None
        self.index_ip = None  # Índice para producto interno (similaridad coseno)
        self.metadata = IndexMetadata(
            embedding_dim=embedding_dim,
            index_type=index_type,
            created_at=datetime.now().isoformat()
        )
        
        # Tracking de vectores
        self._ids = []
        self._texts = []
        self._sources = []
        self._embeddings = []  # Guardar embeddings para fallback
        self._id_to_index = {}  # Mapeo de numeric_id a índice
        
        # Crear o cargar índice
        self._init_index()
    
    def _init_index(self):
        """Inicializa el índice FAISS con soporte para IndexIDMap"""
        if not FAISS_AVAILABLE:
            logger.warning("FAISS no disponible. Usando modo fallback.")
            self.index = None
            self.index_ip = None
            return
        
        # Crear índice según tipo
        try:
            if self.index_type == "flat":
                # Índice plano base (se envolverá con IndexIDMap)
                base_index = faiss.IndexFlatL2(self.embedding_dim)
                self.index = faiss.IndexIDMap(base_index)
                
                # También crear índice de producto interno para similaridad coseno
                base_ip = faiss.IndexFlatIP(self.embedding_dim)
                self.index_ip = faiss.IndexIDMap(base_ip)
                
            elif self.index_type == "ivf":
                # Índice IVF (aproximado, más rápido para grandes volúmenes)
                quantizer = faiss.IndexFlatL2(self.embedding_dim)
                base_index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
                self.index = faiss.IndexIDMap(base_index)
                
                quantizer_ip = faiss.IndexFlatIP(self.embedding_dim)
                base_ip = faiss.IndexIVFFlat(quantizer_ip, self.embedding_dim, 100)
                self.index_ip = faiss.IndexIDMap(base_ip)
                
            elif self.index_type == "hnsw":
                # Índice HNSW (gráfico, muy rápido)
                base_index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
                self.index = faiss.IndexIDMap(base_index)
                
                base_ip = faiss.IndexHNSWFlat(self.embedding_dim, 32)
                self.index_ip = faiss.IndexIDMap(base_ip)
            
            logger.info(f"Índice {self.index_type} inicializado con IndexIDMap (dim: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"Error inicializando índice FAISS: {e}")
            self.index = None
            self.index_ip = None
    
    def _optimize_index_type(self):
        """
        Optimiza automáticamente el tipo de índice según el volumen de datos
        Se llama después de cargar el índice para verificar si necesita actualización
        """
        if not self.auto_optimize:
            return
            
        num_vectors = len(self._ids)
        
        # Si hay más de 50k vectores y estamos en flat, sugerir IVF
        if num_vectors > self.HNSW_THRESHOLD_IVF and self.index_type == "flat":
            logger.info(f"Detectados {num_vectors} vectores. Recomendado usar índice IVF o HNSW")
        
        # Si hay más de 10k vectores y estamos en flat, sugerir HNSW
        elif num_vectors > self.HNSW_THRESHOLD and self.index_type == "flat":
            logger.info(f"Detectados {num_vectors} vectores. Considerar usar índice HNSW para mejor rendimiento")
    
    def is_trained(self) -> bool:
        """Verifica si el índice está entrenado"""
        if self.index is None:
            return True  # Fallback siempre listo
        if hasattr(self.index, 'is_trained'):
            return self.index.is_trained
        return True
    
    def train(self, vectors: np.ndarray):
        """
        Entrena el índice con vectores de ejemplo
        
        Args:
            vectors: Matriz de vectores para entrenamiento
        """
        if not FAISS_AVAILABLE or self.index is None:
            return
        
        vectors = np.asarray(vectors, dtype=np.float32)
        
        if self.index_type == "ivf" and not self.is_trained():
            logger.info("Entrenando índice IVF...")
            self.index.train(vectors)
            if self.index_ip is not None:
                self.index_ip.train(vectors)
            logger.info("Índice entrenado")
    
    def add_vectors(
        self, 
        vectors: np.ndarray, 
        texts: List[str],
        ids: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        use_compression: bool = True
    ):
        """
        Añade vectores al índice
        
        Args:
            vectors: Matriz de vectores (n, dim)
            texts: Textos correspondientes a cada vector
            IDs opcionales para cada vector
            sources: Fuentes opcionales para cada vector
            use_compression: Si True, comprime a float16 para ahorrar RAM
        """
        if vectors.size == 0:
            logger.warning("No hay vectores para añadir")
            return
        
        vectors = np.asarray(vectors, dtype=np.float32)
        
        # Compresión opcional a float16 para ahorrar RAM
        if use_compression:
            vectors = vectors.astype(np.float16)
        
        # Normalizar para similaridad coseno
        norms = np.linalg.norm(vectors.astype(np.float32), axis=1, keepdims=True)
        norms[norms == 0] = 1  # Evitar división por cero
        vectors_normalized = (vectors / norms).astype(np.float32)
        
        # Generar IDs numéricos para FAISS IndexIDMap
        n = len(texts)
        if ids is None:
            start_id = len(self._ids)
            numeric_ids = np.arange(start_id, start_id + n, dtype=np.int64)
            ids = [str(i) for i in numeric_ids]
        else:
            # Convertir IDs a numéricos para IndexIDMap
            try:
                numeric_ids = np.array([int(i.split('_')[-1]) if '_' in i else int(i) for i in ids], dtype=np.int64)
            except:
                numeric_ids = np.arange(len(self._ids), len(self._ids) + n, dtype=np.int64)
        
        # Añadir al índice FAISS con IDs
        if FAISS_AVAILABLE and self.index is not None:
            self.index.add_with_ids(vectors.astype(np.float32), numeric_ids)
            if self.index_ip is not None:
                self.index_ip.add_with_ids(vectors_normalized, numeric_ids)
        
        # Guardar tracking
        if sources is None:
            sources = [""] * n
        
        # Poblar mapeo de numeric_id a índice
        for i, nid in enumerate(numeric_ids):
            self._id_to_index[int(nid)] = len(self._ids) + i
        
        self._ids.extend(ids)
        self._texts.extend(texts)
        self._sources.extend(sources)
        
        # Guardar embeddings para fallback (siempre en float32 para cálculos)
        self._embeddings.extend(vectors.astype(np.float32).tolist())
        
        # Actualizar metadatos
        self.metadata.num_vectors = len(self._ids)
        self.metadata.last_updated = datetime.now().isoformat()
        
        # Verificar si necesitamos optimizar
        self._optimize_index_type()
        
        logger.info(f"Añadidos {n} vectores al índice (total: {self.metadata.num_vectors})")
    
    def search(
        self, 
        query_vector: np.ndarray, 
        k: int = 5,
        min_score: float = 0.0,
        use_cosine: bool = True
    ) -> List[Dict]:
        """
        Busca vectores similares
        
        Args:
            query_vector: Vector de query
            k: Número de resultados
            min_score: Score mínimo de similaridad
            use_cosine: Usar similaridad coseno (True) o L2 (False)
            
        Returns:
            Lista de resultados con texto, score, id y fuente
        """
        if len(self._ids) == 0:
            logger.warning("Índice vacío")
            return []
        
        query_vector = np.asarray(query_vector, dtype=np.float32)
        
        # Asegurar que es 1D
        if query_vector.ndim > 1:
            query_vector = query_vector.flatten()
        
        # Reshaping para FAISS
        query_vector = query_vector.reshape(1, -1)
        
        results = []
        
        if FAISS_AVAILABLE and self.index is not None and self.index_ip is not None:
            if use_cosine:
                # Normalizar query para coseno
                query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
                distances, indices = self.index_ip.search(query_norm, k)
                # El score ya es similaridad coseno (producto interno de vectores normalizados)
                scores = distances[0]
            else:
                distances, indices = self.index.search(query_vector, k)
                # Distancia L2 (menor es mejor), convertir a score (mayor es mejor)
                scores = 1 / (1 + distances[0])
            
            # Procesar resultados
            for i, (idx, score) in enumerate(zip(indices[0], scores)):
                if idx < 0:
                    continue
                if score < min_score:
                    continue
                
                # IndexIDMap devuelve el numeric_id, necesitamos encontrar el índice real
                if hasattr(self, '_id_to_index'):
                    real_idx = self._id_to_index.get(int(idx), -1)
                else:
                    real_idx = int(idx)
                
                if real_idx < 0 or real_idx >= len(self._ids):
                    continue
                    
                results.append({
                    "id": self._ids[real_idx],
                    "text": self._texts[real_idx],
                    "source": self._sources[real_idx] if real_idx < len(self._sources) else "",
                    "similarity": float(score) if use_cosine else float(score),
                    "score": float(score)
                })
        else:
            # Fallback: búsqueda lineal con numpy
            results = self._search_fallback(query_vector.flatten(), k, min_score)
        
        return results
    
    def _search_fallback(
        self, 
        query_vector: np.ndarray, 
        k: int,
        min_score: float
    ) -> List[Dict]:
        """
        Búsqueda fallback usando numpy (sin FAISS)
        
        Implementa búsqueda de similaridad coseno real
        """
        if not hasattr(self, '_embeddings') or len(self._embeddings) == 0:
            logger.warning("No hay embeddings disponibles para fallback")
            return []
        
        try:
            # Convertir embeddings a numpy array
            embeddings = np.array(self._embeddings, dtype=np.float32)
            
            if embeddings.shape[0] == 0:
                return []
            
            # Normalizar query
            query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
            
            # Calcular similaridad coseno (producto punto de vectores normalizados)
            # embeddings ya debería estar normalizado, pero por seguridad lo normalizamos
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1
            embeddings_norm = embeddings / norms
            
            # Calcular similitud
            similarities = embeddings_norm @ query_norm
            
            # Obtener los k mejores
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                
                if score < min_score:
                    continue
                
                results.append({
                    "id": self._ids[idx],
                    "text": self._texts[idx],
                    "source": self._sources[idx] if idx < len(self._sources) else "",
                    "similarity": score,
                    "score": score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda fallback: {e}")
            return []
    
    def search_hybrid(
        self,
        query_vector: np.ndarray,
        query_text: str,
        k: int = 5,
        min_score: float = 0.0,
        keyword_boost: float = 0.1,
        use_cosine: bool = True
    ) -> List[Dict]:
        """
        Búsqueda híbrida: combina búsqueda vectorial con palabras clave
        
        Args:
            query_vector: Vector de query
            query_text: Texto de la query para búsqueda de keywords
            k: Número de resultados
            min_score: Score mínimo
            keyword_boost: Boost adicional por encontrar keywords en el texto
            use_cosine: Usar similaridad coseno
            
        Returns:
            Lista de resultados con scores combinados
        """
        # Primero buscar por vectores
        vector_results = self.search(query_vector, k=k*2, min_score=min_score, use_cosine=use_cosine)
        
        if not vector_results:
            return []
        
        # Extraer keywords de la query (simple: palabras de más de 3 caracteres)
        query_keywords = set(word.lower() for word in query_text.split() if len(word) > 3)
        
        #boost de scores por keywords
        for result in vector_results:
            text_lower = result["text"].lower()
            
            # Contar keywords encontrados
            keyword_matches = sum(1 for kw in query_keywords if kw in text_lower)
            
            # Aplicar boost
            keyword_bonus = keyword_matches * keyword_boost
            result["keyword_bonus"] = keyword_bonus
            
            # Score combinado
            result["score"] = result["score"] + keyword_bonus
            result["keywords_matched"] = keyword_matches
        
        # Reordenar por score combinado
        vector_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Retornar top k
        return vector_results[:k]
    
    def save(self, path: Optional[str] = None):
        """
        Guarda el índice a disco
        
        Args:
            path: Ruta opcional
        """
        path = path or self.index_path
        
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else "data", exist_ok=True)
        
        # Guardar índice FAISS
        if FAISS_AVAILABLE and self.index is not None:
            try:
                # Guardar el índice base (IndexIDMap guarda los IDs automáticamente)
                faiss.write_index(self.index, path)
                if self.index_ip is not None:
                    faiss.write_index(self.index_ip, path + ".ip")
            except Exception as e:
                logger.error(f"Error guardando índice FAISS: {e}")
        
        # Guardar metadatos
        meta_path = path + ".json"
        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                # Guardar estructura completa
                data = {
                    "metadata": asdict(self.metadata),
                    "ids": self._ids,
                    "texts": self._texts,
                    "sources": self._sources,
                    "embeddings": self._embeddings,
                    "id_to_index": {str(k): v for k, v in self._id_to_index.items()}
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando metadatos: {e}")
        
        logger.info(f"Índice guardado en {path}")
    
    def load(self, path: Optional[str] = None) -> bool:
        """
        Carga el índice desde disco
        
        Args:
            path: Ruta opcional
            
        Returns:
            True si se cargó correctamente
        """
        path = path or self.index_path
        
        if not os.path.exists(path):
            logger.warning(f"Índice no encontrado: {path}")
            return False
        
        meta_path = path + ".json"
        
        if not os.path.exists(meta_path):
            logger.warning(f"Metadatos no encontrados: {meta_path}")
            return False
        
        try:
            # Cargar índice FAISS
            if FAISS_AVAILABLE:
                try:
                    self.index = faiss.read_index(path)
                    if os.path.exists(path + ".ip"):
                        self.index_ip = faiss.read_index(path + ".ip")
                except Exception as e:
                    logger.error(f"Error cargando índice FAISS: {e}")
            
            # Cargar metadatos
            with open(meta_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = IndexMetadata(**data.get("metadata", {}))
            self._ids = data.get("ids", [])
            self._texts = data.get("texts", [])
            self._sources = data.get("sources", [])
            self._embeddings = data.get("embeddings", [])
            
            # Cargar mapeo de numeric_id a índice
            id_to_index_data = data.get("id_to_index", {})
            self._id_to_index = {int(k): v for k, v in id_to_index_data.items()}
            
            # Verificar si necesitamos optimizar
            self._optimize_index_type()
            
            logger.info(f"Índice cargado: {len(self._ids)} vectores")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando índice: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del índice"""
        return {
            "num_vectors": len(self._ids),
            "embedding_dim": self.embedding_dim,
            "index_type": self.index_type,
            "faiss_available": FAISS_AVAILABLE,
            "created_at": self.metadata.created_at,
            "last_updated": self.metadata.last_updated,
            "embeddings_stored": len(self._embeddings) if hasattr(self, '_embeddings') else 0
        }
    
    def clear(self):
        """Limpia el índice"""
        if FAISS_AVAILABLE and self.index is not None:
            # Crear nuevo índice vacío
            self._init_index()
        
        self._ids = []
        self._texts = []
        self._sources = []
        self._embeddings = []
        self._id_to_index = {}
        
        self.metadata.num_vectors = 0
        self.metadata.last_updated = datetime.now().isoformat()
        
        logger.info("Índice limpiado")


# ============================================
# Funciones Helper para RAG
# ============================================

def format_rag_context(
    results: List[Dict],
    include_source: bool = True,
    include_score: bool = False,
    max_length: Optional[int] = None
) -> str:
    """
    Formatea resultados de búsqueda como contexto para RAG
    
    Args:
        results: Lista de resultados de search()
        include_source: Incluir fuente en el formato
        include_score: Incluir score de similaridad
        max_length: Longitud máxima del contexto (truncar si excede)
        
    Returns:
        String formateado con el contexto
    """
    if not results:
        return ""
    
    context_parts = []
    
    for i, r in enumerate(results, 1):
        part = ""
        
        if include_source and r.get("source"):
            part = f"[Fuente {i}: {r['source']}]\n"
        elif include_source:
            part = f"[Resultado {i}]\n"
        
        part += r.get("text", "")
        
        if include_score:
            score = r.get("similarity", r.get("score", 0))
            part += f"\n(score: {score:.3f})"
        
        context_parts.append(part)
    
    context = "\n\n".join(context_parts)
    
    # Truncar si excede max_length
    if max_length and len(context) > max_length:
        context = context[:max_length] + "\n...(truncado)"
    
    return context


def build_rag_prompt(
    query: str,
    results: List[Dict],
    system_prompt: Optional[str] = None,
    include_sources: bool = True
) -> Tuple[str, str]:
    """
    Construye un prompt para RAG con contexto y query
    
    Args:
        query: Pregunta del usuario
        results: Resultados de búsqueda
        system_prompt: Prompt de sistema personalizado
        include_sources: Incluir fuentes en el contexto
        
    Returns:
        Tupla (system_prompt, user_prompt)
    """
    context = format_rag_context(results, include_source=include_sources)
    
    if system_prompt is None:
        system_prompt = """Eres un asistente útil que responde preguntas basándose en el contexto proporcionado.
Si no tienes información suficiente en el contexto, indica que no sabes la respuesta."""
    
    user_prompt = f"""Contexto:
{context}

Pregunta: {query}

Respuesta:"""
    
    return system_prompt, user_prompt


# ============================================
# Instancia Global y Funciones de Convenience
# ============================================

# Instancia global
_index = None


def get_vector_index(
    embedding_dim: int = 384,
    index_type: str = "flat",
    force_new: bool = False,
    auto_optimize: bool = True
) -> VectorIndex:
    """
    Obtiene el índice vectorial global
    
    Args:
        embedding_dim: Dimensión de embeddings
        index_type: Tipo de índice
        force_new: Si True, crea nuevo índice
        auto_optimize: Si True, optimiza automáticamente para grandes volúmenes
        
    Returns:
        Instancia de VectorIndex
    """
    global _index
    
    if _index is None or force_new:
        _index = VectorIndex(
            embedding_dim=embedding_dim,
            index_type=index_type,
            auto_optimize=auto_optimize
        )
        
        # Intentar cargar índice existente
        _index.load()
    
    return _index


def search_vector_index(
    query: str,
    embedding_model,
    k: int = 5,
    min_score: float = 0.3,
    hybrid: bool = False,
    keyword_boost: float = 0.1
) -> List[Dict]:
    """
    Función de conveniencia para buscar en el índice
    
    Args:
        query: Texto de query
        embedding_model: Modelo de embeddings
        k: Número de resultados
        min_score: Score mínimo
        hybrid: Usar búsqueda híbrida
        keyword_boost: Boost para keywords en búsqueda híbrida
        
    Returns:
        Lista de resultados
    """
    index = get_vector_index()
    
    # Generar embedding
    query_embedding = embedding_model.embed(query)
    
    # Buscar
    if hybrid:
        results = index.search_hybrid(
            query_vector=query_embedding,
            query_text=query,
            k=k,
            min_score=min_score,
            keyword_boost=keyword_boost
        )
    else:
        results = index.search(query_embedding, k=k, min_score=min_score)
    
    return results


def rebuild_vector_index(
    documents: Dict[str, str],
    embedding_model,
    batch_size: int = 32,
    index_type: str = "flat",
    show_progress: bool = True
):
    """
    Reconstruye el índice vectorial con nuevos documentos
    
    Args:
        documents: Diccionario {filename: text}
        embedding_model: Modelo de embeddings
        batch_size: Tamaño de batch
        index_type: Tipo de índice ('flat', 'ivf', 'hnsw')
        show_progress: Mostrar barra de progreso
    """
    from .text_chunker import chunk_text
    
    logger.info("Reconstruyendo índice vectorial...")
    
    # Determinar tipo de índice automáticamente si hay muchos documentos
    num_docs = sum(len(chunk_text(text)) for text in documents.values())
    
    if index_type == "auto":
        if num_docs > 50000:
            index_type = "ivf"
            logger.info(f"Índice automático: IVF ({num_docs} documentos)")
        elif num_docs > 10000:
            index_type = "hnsw"
            logger.info(f"Índice automático: HNSW ({num_docs} documentos)")
        else:
            index_type = "flat"
            logger.info(f"Índice automático: Flat ({num_docs} documentos)")
    
    # Obtener índice (forzar nuevo)
    index = get_vector_index(force_new=True, index_type=index_type)
    
    all_texts = []
    all_sources = []
    all_ids = []
    
    # Procesar cada documento
    doc_id = 0
    for filename, text in documents.items():
        # Chunking
        chunks = chunk_text(text)
        
        for chunk in chunks:
            all_texts.append(chunk)
            all_sources.append(filename)
            all_ids.append(f"{filename}_{doc_id}")
            doc_id += 1
    
    if not all_texts:
        logger.warning("No hay texto para indexar")
        return
    
    logger.info(f"Generando embeddings para {len(all_texts)} chunks...")
    
    # Generar embeddings en batches con progreso
    embeddings = embedding_model.embed_batch(
        all_texts, 
        batch_size=batch_size,
        show_progress=show_progress
    )
    
    # Añadir al índice
    index.add_vectors(
        vectors=embeddings,
        texts=all_texts,
        ids=all_ids,
        sources=all_sources
    )
    
    # Guardar
    index.save()
    
    logger.info(f"Índice reconstruido con {len(all_texts)} chunks (tipo: {index_type})")
    
    return index


def create_vector_index_from_existing(
    embedding_dim: int = 384,
    index_type: str = "hnsw"
) -> VectorIndex:
    """
    Crea un nuevo índice con el tipo especificado (sin cargar existente)
    
    Args:
        embedding_dim: Dimensión de embeddings
        index_type: Tipo de índice
        
    Returns:
        Nueva instancia de VectorIndex
    """
    return VectorIndex(
        embedding_dim=embedding_dim,
        index_type=index_type,
        force_new=True
    )

