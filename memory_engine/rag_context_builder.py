"""
RAG Context Builder - Constructor de Contexto para RAG
=====================================================
IA Local Vargas - Memory Engine
Sistema para construir contexto eficiente para LLMs
"""

import logging
from typing import List, Dict, Optional, Set, Tuple
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


# Estimación aproximada de tokens (promedio: 4 caracteres por token)
CHARS_PER_TOKEN = 4


class RAGContextBuilder:
    """
    Constructor de contexto para Retrieval-Augmented Generation
    """
    
    def __init__(
        self,
        max_tokens: int = 4000,
        overlap_chunks: bool = True,
        deduplicate: bool = True,
        rank_by: str = "score"
    ):
        """
        Inicializa el builder de contexto
        
        Args:
            max_tokens: Máximo de tokens en el contexto
            overlap_chunks: Mantener overlap entre chunks
            deduplicate: Eliminar chunks duplicados
            rank_by: Método de ranking ('score', 'position', 'diversity')
        """
        self.max_tokens = max_tokens
        self.overlap_chunks = overlap_chunks
        self.deduplicate = deduplicate
        self.rank_by = rank_by
        
        # Tracking de fuentes
        self._source_counts = defaultdict(int)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estima el número de tokens en un texto
        
        Args:
            text: Texto a estimar
            
        Returns:
            Número aproximado de tokens
        """
        return len(text) // CHARS_PER_TOKEN
    
    def deduplicate_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Elimina chunks duplicados o muy similares
        
        Args:
            chunks: Lista de chunks con texto y metadata
            
        Returns:
            Lista de chunks deduplicados
        """
        if not self.deduplicate:
            return chunks
        
        seen_texts = set()
        unique_chunks = []
        
        for chunk in chunks:
            # Normalizar texto para comparación
            normalized = chunk.get("text", "").lower().strip()
            
            # Crear fingerprint (primeras y últimas palabras)
            words = normalized.split()
            if len(words) > 10:
                fingerprint = " ".join(words[:5] + words[-5:])
            else:
                fingerprint = normalized
            
            # Verificar si es duplicado
            if fingerprint not in seen_texts:
                seen_texts.add(fingerprint)
                unique_chunks.append(chunk)
        
        logger.info(f"Deduplicación: {len(chunks)} -> {len(unique_chunks)} chunks")
        return unique_chunks
    
    def rank_chunks(
        self, 
        chunks: List[Dict], 
        query: str
    ) -> List[Dict]:
        """
        Ranking de chunks según diversos criterios
        
        Args:
            chunks: Lista de chunks
            query: Query original
            
        Returns:
            Chunks ordenados por relevancia
        """
        if not chunks:
            return []
        
        if self.rank_by == "score":
            # Ordenar por score de similaridad
            return sorted(chunks, key=lambda x: x.get("score", 0), reverse=True)
        
        elif self.rank_by == "position":
            # Preferir chunks al inicio (probablemente más relevantes)
            return sorted(chunks, key=lambda x: x.get("chunk_id", 0))
        
        elif self.rank_by == "diversity":
            # Mezclar resultados de diferentes fuentes
            source_order = defaultdict(int)
            ranked = []
            
            remaining = chunks.copy()
            while remaining:
                # Tomar el mejor de cada fuente
                for chunk in remaining[:]:
                    source = chunk.get("metadata", {}).get("source", "unknown")
                    if source_order[source] == 0:
                        ranked.append(chunk)
                        source_order[source] += 1
                        remaining.remove(chunk)
                        break
                else:
                    # Si no se encontró diversidad, tomar el primero
                    ranked.append(remaining.pop(0))
            
            return ranked
        
        return chunks
    
    def build_context(
        self,
        results: List[Dict],
        query: str,
        max_chars: Optional[int] = None
    ) -> str:
        """
        Construye el contexto para el LLM
        
        Args:
            results: Resultados de búsqueda
            query: Query original
            max_chars: Límite de caracteres (opcional)
            
        Returns:
            Contexto formateado
        """
        if not results:
            return ""
        
        # Deduplicar
        chunks = self.deduplicate_chunks(results)
        
        # Ranking
        chunks = self.rank_chunks(chunks, query)
        
        # Calcular límites
        if max_chars is None:
            max_chars = self.max_tokens * CHARS_PER_TOKEN
        
        # Construir contexto
        context_parts = []
        total_chars = 0
        source_used = set()
        
        for chunk in chunks:
            text = chunk.get("text", "")
            source = chunk.get("metadata", {}).get("source", "")
            score = chunk.get("score", 0)
            
            # Verificar límite de caracteres
            if total_chars + len(text) > max_chars:
                remaining = max_chars - total_chars
                if remaining < 100:  # No merece la pena si es muy pequeño
                    break
                text = text[:remaining] + "..."
            
            # Agregar al contexto
            header = f"[{source}] (Relevancia: {score:.2f})"
            context_parts.append(f"{header}\n{text}")
            
            total_chars += len(header) + len(text) + 2
            source_used.add(source)
            
            # Verificar límite de tokens
            if self.estimate_tokens("\n\n".join(context_parts)) > self.max_tokens:
                break
        
        return "\n\n---\n\n".join(context_parts)
    
    def build_context_with_sources(
        self,
        results: List[Dict],
        query: str
    ) -> Tuple[str, Dict]:
        """
        Construye contexto y retorna información de fuentes
        
        Args:
            results: Resultados de búsqueda
            query: Query original
            
        Returns:
            Tupla (contexto, info_fuentes)
        """
        context = self.build_context(results, query)
        
        # Recopilar información de fuentes
        sources_info = defaultdict(lambda: {"count": 0, "max_score": 0})
        
        for chunk in results:
            source = chunk.get("metadata", {}).get("source", "unknown")
            score = chunk.get("score", 0)
            
            sources_info[source]["count"] += 1
            sources_info[source]["max_score"] = max(
                sources_info[source]["max_score"],
                score
            )
        
        return context, dict(sources_info)
    
    def format_for_llm(
        self,
        context: str,
        query: str,
        include_instructions: bool = True
    ) -> str:
        """
        Formatea el contexto para el LLM
        
        Args:
            context: Contexto construido
            query: Query original
            include_instructions: Incluir instrucciones de uso
            
        Returns:
            Prompt formateado
        """
        prompt_parts = []
        
        if include_instructions:
            prompt_parts.append("""Usa la siguiente información de los documentos para responder la pregunta.
Si la información no es suficiente, indica que no tienes suficiente información.""")
        
        prompt_parts.append(f"📚 **INFORMACIÓN DE DOCUMENTOS:**\n{context}")
        
        prompt_parts.append(f"❓ **PREGUNTA:**\n{query}")
        
        return "\n\n".join(prompt_parts)


# Instancia global
_rag_builder = None


def get_rag_builder(
    max_tokens: int = 4000,
    deduplicate: bool = True
) -> RAGContextBuilder:
    """
    Obtiene el builder de contexto RAG global
    
    Args:
        max_tokens: Máximo de tokens
        deduplicate: Eliminar duplicados
        
    Returns:
        Instancia de RAGContextBuilder
    """
    global _rag_builder
    
    if _rag_builder is None:
        _rag_builder = RAGContextBuilder(
            max_tokens=max_tokens,
            deduplicate=deduplicate
        )
    
    return _rag_builder


def build_rag_context(
    query: str,
    search_results: List[Dict],
    max_tokens: int = 4000,
    include_sources: bool = True
) -> str:
    """
    Función de conveniencia para construir contexto RAG
    
    Args:
        query: Query del usuario
        search_results: Resultados de búsqueda semántica
        max_tokens: Máximo de tokens
        include_sources: Incluir información de fuentes
        
    Returns:
        Contexto formateado
    """
    builder = RAGContextBuilder(max_tokens=max_tokens)
    return builder.build_context(search_results, query)


def get_relevant_documents_for_rag(
    query: str,
    documents: Dict[str, str],
    n_results: int = 3,
    max_tokens: int = 4000
) -> Tuple[str, Dict]:
    """
    Obtiene documentos relevantes para RAG de forma completa
    
    Args:
        query: Query del usuario
        documents: Diccionario de documentos
        n_results: Número de resultados
        max_tokens: Máximo de tokens en contexto
        
    Returns:
        Tupla (contexto, info_fuentes)
    """
    from .semantic_search import search_documents_semantic
    
    # Buscar documentos
    results = search_documents_semantic(
        query=query,
        documents=documents,
        n_results=n_results,
        min_score=0.2
    )
    
    if not results:
        return "", {}
    
    # Construir contexto
    builder = RAGContextBuilder(max_tokens=max_tokens)
    context, sources_info = builder.build_context_with_sources(results, query)
    
    return context, sources_info


# Funciones de compatibilidad
def get_relevant_documents(
    query: str,
    max_chars: int = 5000,
    n_results: int = 3
) -> str:
    """
    Obtiene documentos relevantes (compatibilidad)
    
    Args:
        query: Query
        max_chars: Caracteres máximos
        n_results: Resultados
        
    Returns:
        Contexto
    """
    from documents import search_documents_semantic, get_cache
    
    # Obtener documentos del caché
    cache = get_cache()
    
    if not cache:
        return ""
    
    # Buscar
    results = search_documents_semantic(
        query,
        n_results=n_results,
        min_score=0.3
    )
    
    if not results:
        return ""
    
    # Construir contexto
    builder = RAGContextBuilder(max_tokens=max_chars // CHARS_PER_TOKEN)
    return builder.build_context(results, query)


def format_rag_results(results: List[Dict], max_results: int = 3) -> str:
    """
    Formatea resultados de RAG para display
    
    Args:
        results: Lista de resultados
        max_results: Máximo a mostrar
        
    Returns:
        String formateado
    """
    if not results:
        return "No se encontró información relevante."
    
    output = [f"📚 **Resultados relevantes ({len(results)}):**\n"]
    
    for i, r in enumerate(results[:max_results], 1):
        source = r.get("metadata", {}).get("source", "Unknown")
        score = r.get("score", 0)
        text = r.get("text", "")[:200]
        
        output.append(
            f"{i}. [{source}] (Score: {score:.2f})\n"
            f"   {text}...\n"
        )
    
    return "\n".join(output)

