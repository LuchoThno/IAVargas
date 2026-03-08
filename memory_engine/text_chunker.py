"""
Text Chunker - Segmentación de Texto Semántica
=============================================
IA Local Vargas - Memory Engine
Divide texto en chunks semánticamente coherentes
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChunkConfig:
    """Configuración para el chunking de texto"""
    chunk_size: int = 500
    overlap: int = 50
    min_chunk_size: int = 100
    max_chunk_size: int = 1000
    
    def __post_init__(self):
        # Validar parámetros
        if self.chunk_size < self.min_chunk_size:
            self.chunk_size = self.min_chunk_size
        if self.overlap >= self.chunk_size:
            self.overlap = self.chunk_size // 4


class TextChunker:
    """
    Clase para dividir texto en chunks semánticamente coherentes
    """
    
    # Separadores por prioridad (del más grande al más pequeño)
    PARAGRAPH_SEPARATORS = ['\n\n', '\r\n\r\n']
    LINE_SEPARATORS = ['\n', '\r\n', '\r']
    SENTENCE_ENDINGS = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        Inicializa el chunker
        
        Args:
            config: Configuración de chunking
        """
        self.config = config or ChunkConfig()
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        Divide texto en párrafos
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de párrafos
        """
        # Intentar dividir por párrafos primero
        for sep in self.PARAGRAPH_SEPARATORS:
            if sep in text:
                paragraphs = text.split(sep)
                # Filtrar párrafos vacíos
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
                if len(paragraphs) > 1:
                    return paragraphs
        
        # Si no hay párrafos, dividir por líneas
        for sep in self.LINE_SEPARATORS:
            if sep in text:
                lines = text.split(sep)
                lines = [l.strip() for l in lines if l.strip()]
                if len(lines) > 1:
                    return lines
        
        # Si es texto corto, devolver como una sola pieza
        return [text.strip()] if text.strip() else []
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Divide texto en oraciones
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de oraciones
        """
        # Usar regex para dividir por oraciones
        # Considera puntuación final + espacio
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        
        # Filtrar oraciones vacías o muy cortas
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def merge_small_chunks(self, chunks: List[str], min_size: int = None) -> List[str]:
        """
        Fusiona chunks muy pequeños con el anterior
        
        Args:
            chunks: Lista de chunks
            min_size: Tamaño mínimo de chunk
            
        Returns:
            Lista de chunks fusionados
        """
        if min_size is None:
            min_size = self.config.min_chunk_size
        
        # Asegurar que min_size sea un entero
        try:
            min_size = int(min_size)
        except (TypeError, ValueError):
            min_size = self.config.min_chunk_size
        
        if not chunks:
            return []
        
        merged = [chunks[0]]
        
        for chunk in chunks[1:]:
            last_len = len(merged[-1]) if merged else 0
            if last_len < min_size:
                # Fusionar con el anterior
                merged[-1] = merged[-1] + " " + chunk
            else:
                merged.append(chunk)
        
        return merged
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Divide el texto en chunks semánticamente coherentes
        
        Args:
            text: Texto a dividir
            chunk_size: Tamaño máximo de cada chunk (opcional, usa config)
            overlap: Cantidad de overlap entre chunks (opcional, usa config)
            
        Returns:
            Lista de chunks
        """
        # Usar valores de config si no se especifican
        if chunk_size is None:
            chunk_size = self.config.chunk_size
        if overlap is None:
            overlap = self.config.overlap
        
        if not text or not text.strip():
            return []
        
        # Si el texto es más pequeño que el chunk, devolverlo completo
        if len(text) <= chunk_size:
            return [text.strip()]
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Si no llegamos al final, intentar dividir en punto lógico
            if end < text_length:
                # Buscar el mejor punto de división
                end = self._find_best_split_point(text, start, end)
            
            # Asegurar que no excedamos el texto
            if end > text_length:
                end = text_length
            
            # Extraer el chunk
            chunk = text[start:end].strip()
            
            if chunk and len(chunk) >= self.config.min_chunk_size:
                chunks.append(chunk)
            elif chunk:
                # Si es muy pequeño, intentar fusionar
                if chunks:
                    chunks[-1] = chunks[-1] + " " + chunk
                else:
                    chunks.append(chunk)
            
            # Mover el inicio con overlap
            new_start = end - overlap
            
            # Asegurar progreso (evitar loops infinitos)
            if new_start <= start:
                # Si no hay progreso, avanzar al final del texto
                start = text_length
            else:
                start = new_start
        
        # Fusionar chunks muy pequeños
        chunks = self.merge_small_chunks(chunks)
        
        # Recortar chunks que excedan el máximo
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.config.max_chunk_size:
                # Dividir chunks muy grandes
                sub_chunks = self._split_oversized_chunk(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _find_best_split_point(self, text: str, start: int, end: int) -> int:
        """
        Encuentra el mejor punto para dividir el texto
        
        Args:
            text: Texto completo
            start: Inicio del chunk
            end: Fin tentativo del chunk
            
        Returns:
            Mejor punto de división
        """
        # Prioridad 1: Fin de oración
        for ending in self.SENTENCE_ENDINGS:
            last_ending = text.rfind(ending, start, end)
            if last_ending > start:
                return last_ending + len(ending)
        
        # Prioridad 2: Fin de línea
        for sep in self.LINE_SEPARATORS:
            last_sep = text.rfind(sep, start, end)
            if last_sep > start:
                return last_sep + len(sep)
        
        # Prioridad 3: Fin de palabra (evitar cortar palabras)
        last_space = text.rfind(' ', start, end)
        if last_space > start:
            return last_space
        
        # Si nada funciona, devolver el punto original
        return end
    
    def _split_oversized_chunk(self, chunk: str) -> List[str]:
        """
        Divide un chunk que excede el tamaño máximo
        
        Args:
            chunk: Chunk muy grande
            
        Returns:
            Lista de sub-chunks
        """
        # Dividir por oraciones
        sentences = self.split_by_sentences(chunk)
        
        sub_chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.config.max_chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    sub_chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            sub_chunks.append(current_chunk.strip())
        
        return sub_chunks if sub_chunks else [chunk]
    
    def chunk_by_structure(self, text: str) -> List[Dict]:
        """
        Divide el texto respetando su estructura (para RAG)
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de diccionarios con chunks y metadatos
        """
        chunks_data = []
        
        # Primero intentar dividir por secciones
        sections = self._extract_sections(text)
        
        for i, section in enumerate(sections):
            section_chunks = self.chunk_text(section['content'])
            
            for j, chunk in enumerate(section_chunks):
                chunks_data.append({
                    'text': chunk,
                    'section': section.get('title', ''),
                    'section_id': i,
                    'chunk_id': j,
                    'char_count': len(chunk),
                    'word_count': len(chunk.split())
                })
        
        return chunks_data
    
    def _extract_sections(self, text: str) -> List[Dict]:
        """
        Extrae secciones del texto basadas en encabezados
        
        Args:
            text: Texto a procesar
            
        Returns:
            Lista de secciones con título y contenido
        """
        sections = []
        
        # Buscar patrones de encabezados
        # Markdown: # Título, ## Título
        # Texto: TÍTULO en mayúsculas o líneas con ---
        header_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown
            r'^([A-Z][A-Z\s]+)$',  # Mayúsculas
            r'^---+$',  # Líneas horizontales
            r'^\d+\.\s+(.+)$',  # Listas numeradas
        ]
        
        lines = text.split('\n')
        current_section = {'title': '', 'content': ''}
        
        for line in lines:
            is_header = False
            
            for pattern in header_patterns:
                if re.match(pattern, line.strip()):
                    # Guardar sección anterior
                    if current_section['content'].strip():
                        sections.append(current_section)
                    
                    # Nueva sección
                    title = re.sub(r'^#+\s*', '', line.strip())
                    current_section = {'title': title, 'content': ''}
                    is_header = True
                    break
            
            if not is_header:
                current_section['content'] += line + '\n'
        
        # Agregar última sección
        if current_section['content'].strip():
            sections.append(current_section)
        
        # Si no hay secciones, usar el texto completo
        if not sections:
            sections = [{'title': 'General', 'content': text}]
        
        return sections


# Instancia global con configuración por defecto
_chunker = None


def get_text_chunker(config: Optional[ChunkConfig] = None) -> TextChunker:
    """
    Obtiene el chunker de texto (singleton)
    
    Args:
        config: Configuración opcional
        
    Returns:
        Instancia de TextChunker
    """
    global _chunker
    if _chunker is None or config is not None:
        _chunker = TextChunker(config)
    return _chunker


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Función de conveniencia para chunking de texto
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño de chunk
        overlap: Overlap entre chunks
        
    Returns:
        Lista de chunks
    """
    config = ChunkConfig(chunk_size=chunk_size, overlap=overlap)
    chunker = get_text_chunker(config)
    return chunker.chunk_text(text)


def chunk_for_rag(text: str, chunk_size: int = 500) -> List[Dict]:
    """
    Función de conveniencia para chunking con metadatos (RAG)
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño de chunk
        
    Returns:
        Lista de diccionarios con chunks y metadatos
    """
    config = ChunkConfig(chunk_size=chunk_size)
    chunker = get_text_chunker(config)
    return chunker.chunk_by_structure(text)

