"""
Document Loader - Carga de Documentos
=====================================
IA Local Vargas - Memory Engine
Manejo de carga de documentos con soporte paralelo
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

# Tipos de archivo soportados
SUPPORTED_EXTENSIONS = {'.pdf', '.csv', '.xlsx', '.xls', '.txt'}


class DocumentLoader:
    """
    Clase para cargar documentos con procesamiento paralelo
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Inicializa el loader de documentos
        Args:
            max_workers: Número máximo de workers para procesamiento paralelo
        """
        self.max_workers = max_workers
        self._import_handlers()
    
    def _import_handlers(self):
        """Importa los handlers según el tipo de archivo"""
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
        import pandas as pd
        
        self.PdfReader = PdfReader
        self.PdfReadError = PdfReadError
        self.pd = pd
    
    def get_file_hash_chunked(self, filepath: str, chunk_size: int = 8192) -> str:
        """
        Calcula hash del archivo usando bloques (para archivos grandes)
        
        Args:
            filepath: Ruta al archivo
            chunk_size: Tamaño de cada bloque (8KB por defecto)
            
        Returns:
            Hash MD5 del archivo
        """
        import hashlib
        
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash de {filepath}: {e}")
            return ""
    
    def extract_text_from_pdf(self, path: str) -> Tuple[str, bool]:
        """
        Extrae texto de PDF con manejo robusto de errores
        
        Args:
            path: Ruta al archivo PDF
            
        Returns:
            Tupla (texto_extraido, success)
        """
        text = ""
        success = False
        
        try:
            reader = self.PdfReader(path)
            logger.info(f"PDF: {os.path.basename(path)} ({len(reader.pages)} páginas)")
            
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        # Limpiar texto
                        page_text = self._clean_text(page_text)
                        text += f"\n\n--- Página {i+1} ---\n\n"
                        text += page_text
                except Exception as e:
                    logger.warning(f"Error en página {i+1}: {e}")
                    continue
            
            success = bool(text.strip())
            
        except self.PdfReadError as e:
            logger.error(f"PDF corrupto {path}: {e}")
        except Exception as e:
            logger.error(f"Error inesperado extrayendo PDF {path}: {e}")
        
        return text, success
    
    def extract_text_from_csv(self, path: str) -> Tuple[str, bool]:
        """Extrae texto de CSV"""
        text = ""
        success = False
        
        try:
            df = self.pd.read_csv(path)
            text = f"### CSV: {os.path.basename(path)} ###\n"
            text += df.to_string(max_rows=100)
            success = True
        except Exception as e:
            logger.error(f"Error leyendo CSV {path}: {e}")
        
        return text, success
    
    def extract_text_from_xlsx(self, path: str) -> Tuple[str, bool]:
        """Extrae texto de Excel"""
        text = ""
        success = False
        
        try:
            df = self.pd.read_excel(path)
            text = f"### Excel: {os.path.basename(path)} ###\n"
            text += df.to_string(max_rows=100)
            success = True
        except Exception as e:
            logger.error(f"Error leyendo Excel {path}: {e}")
        
        return text, success
    
    def extract_text_from_txt(self, path: str) -> Tuple[str, bool]:
        """Extrae texto de archivos txt"""
        text = ""
        success = False
        
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    text = f.read()
                success = True
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error leyendo TXT {path}: {e}")
                break
        
        return text, success
    
    def process_document(self, path: str) -> Optional[Dict]:
        """
        Procesa un documento según su extensión
        
        Args:
            path: Ruta al documento
            
        Returns:
            Diccionario con información del documento o None si hay error
        """
        ext = os.path.splitext(path)[1].lower()
        
        if ext not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Tipo de archivo no soportado: {ext}")
            return None
        
        # Extraer texto según tipo
        if ext == ".pdf":
            text, success = self.extract_text_from_pdf(path)
        elif ext == ".csv":
            text, success = self.extract_text_from_csv(path)
        elif ext in [".xlsx", ".xls"]:
            text, success = self.extract_text_from_xlsx(path)
        elif ext == ".txt":
            text, success = self.extract_text_from_txt(path)
        else:
            return None
        
        if not success or not text.strip():
            return None
        
        return {
            "filename": os.path.basename(path),
            "filepath": path,
            "extension": ext,
            "text": text,
            "hash": self.get_file_hash_chunked(path),
            "size": os.path.getsize(path),
            "processed": datetime.now().isoformat()
        }
    
    def load_documents_parallel(self, folder: str) -> List[Dict]:
        """
        Carga documentos en paralelo
        
        Args:
            folder: Carpeta con documentos
            
        Returns:
            Lista de diccionarios con documentos procesados
        """
        if not os.path.exists(folder):
            logger.warning(f"Carpeta no existe: {folder}")
            return []
        
        # Obtener archivos
        files = []
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    files.append(path)
        
        if not files:
            logger.info("No hay documentos para procesar")
            return []
        
        logger.info(f"Procesando {len(files)} documento(s) en paralelo...")
        
        results = []
        
        # Procesar en paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_document, path): path 
                for path in files
            }
            
            for future in as_completed(future_to_file):
                path = future_to_file[future]
                try:
                    doc = future.result()
                    if doc:
                        results.append(doc)
                        logger.info(f"✓ {doc['filename']}")
                except Exception as e:
                    logger.error(f"Error procesando {path}: {e}")
        
        return results
    
    def _clean_text(self, text: str) -> str:
        """
        Limpia y normaliza texto
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        if not text:
            return ""
        
        # Eliminar caracteres de control
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Normalizar espacios
        import re
        text = re.sub(r'[ \t]+', ' ', text)  # Múltiples espacios -> uno
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Múltiples saltos -> doble
        
        return text.strip()


# Instancia global con lazy loading
_loader = None


def get_document_loader() -> DocumentLoader:
    """Obtiene el loader de documentos (singleton)"""
    global _loader
    if _loader is None:
        _loader = DocumentLoader()
    return _loader


def load_documents_parallel(folder: str = "documents") -> List[Dict]:
    """Función de conveniencia para cargar documentos en paralelo"""
    loader = get_document_loader()
    return loader.load_documents_parallel(folder)


def get_file_hash(filepath: str) -> str:
    """Función de conveniencia para obtener hash"""
    loader = get_document_loader()
    return loader.get_file_hash_chunked(filepath)

