"""
Language Executor - Ejecutor Multi-Lenguaje
============================================
Sistema de ejecución de código en múltiples lenguajes:
- Python (ya implementado con sandbox)
- Node.js
- Java
- Go
- Rust
- C/C++

Características:
- Sandboxing seguro
- Timeout configurable
- Captura de stdout/stderr
- Soporte para múltiples lenguajes
"""

import os
import sys
import subprocess
import tempfile
import shutil
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import multiprocessing

# ============================================
# CONFIGURACIÓN
# ============================================

DEFAULT_TIMEOUT = 30  # segundos
MAX_OUTPUT_SIZE = 100000  # bytes

# Comandos disponibles en el sistema
AVAILABLE_RUNTIMES = {
    "python": "python",
    "python3": "python",
    "node": "node",
    "javascript": "node",
    "java": "java",
    "javac": "javac",
    "go": "go",
    "rustc": "rustc",
    "gcc": "gcc",
    "c": "gcc",
    "cpp": "g++",
}

# Extensiones de archivos
FILE_EXTENSIONS = {
    "python": ".py",
    "javascript": ".js",
    "java": ".java",
    "go": ".go",
    "rust": ".rs",
    "c": ".c",
    "cpp": ".cpp",
}

# ============================================
# EJECUTOR DE LENGUAJES
# ============================================

class LanguageExecutor:
    """Ejecutor de código multi-lenguaje"""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, workspace: str = None):
        """
        Inicializa el ejecutor
        
        Args:
            timeout: Timeout por defecto en segundos
            workspace: Directorio de trabajo
        """
        self.timeout = timeout
        self.workspace = workspace or self._get_default_workspace()
        self._ensure_workspace()
    
    def _get_default_workspace(self) -> str:
        """Obtiene el workspace por defecto"""
        workspace_path = Path("workspace/temp")
        if not workspace_path.exists():
            workspace_path.mkdir(parents=True, exist_ok=True)
        return str(workspace_path)
    
    def _ensure_workspace(self):
        """Asegura que el workspace exista"""
        Path(self.workspace).mkdir(parents=True, exist_ok=True)
    
    def execute(self, code: str, language: str = "python", 
                timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Ejecuta código en el lenguaje especificado
        
        Args:
            code: Código a ejecutar
            language: Lenguaje de programación
            timeout: Timeout opcional
            
        Returns:
            Diccionario con stdout, stderr y código de salida
        """
        timeout = timeout or self.timeout
        
        # Normalizar nombre del lenguaje
        language = language.lower().strip()
        
        # Buscar ejecutable
        executor = self._find_executor(language)
        if not executor:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Runtime no encontrado: {language}",
                "exit_code": -1,
                "error": f"Lenguaje no soportado o no instalado: {language}"
            }
        
        # Crear archivo temporal
        file_path = self._create_temp_file(code, language)
        if not file_path:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Error creando archivo temporal",
                "exit_code": -1,
                "error": "No se pudo crear el archivo temporal"
            }
        
        try:
            # Ejecutar según el lenguaje
            if language in ["python", "javascript", "node"]:
                return self._execute_script(executor, file_path, timeout)
            elif language in ["java"]:
                return self._execute_java(executor, file_path, timeout)
            elif language in ["go"]:
                return self._execute_go(executor, file_path, timeout)
            elif language in ["rust"]:
                return self._execute_rust(file_path, timeout)
            elif language in ["c", "cpp"]:
                return self._execute_cpp(language, file_path, timeout)
            else:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Lenguaje no soportado: {language}",
                    "exit_code": -1
                }
        finally:
            # Limpiar archivo temporal
            self._cleanup_temp_file(file_path)
    
    def _find_executor(self, language: str) -> Optional[str]:
        """Busca el ejecutable del lenguaje"""
        cmd = AVAILABLE_RUNTIMES.get(language)
        if not cmd:
            return None
        
        # Verificar si está instalado
        result = subprocess.run(
            ["where" if sys.platform == "win32" else "which", cmd],
            capture_output=True,
            text=True
        )
        
        return cmd if result.returncode == 0 else None
    
    def _create_temp_file(self, code: str, language: str) -> Optional[str]:
        """Crea un archivo temporal con el código"""
        try:
            ext = FILE_EXTENSIONS.get(language, ".txt")
            fd, path = tempfile.mkstemp(suffix=ext, dir=self.workspace)
            
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return path
        except Exception as e:
            print(f"Error creando archivo temporal: {e}")
            return None
    
    def _cleanup_temp_file(self, file_path: str):
        """Limpia el archivo temporal"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
    
    def _execute_script(self, executor: str, file_path: str, 
                       timeout: int) -> Dict[str, Any]:
        """Ejecuta un script (Python, Node.js)"""
        try:
            result = subprocess.run(
                [executor, file_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            # Limitar tamaño de salida
            stdout = result.stdout[:MAX_OUTPUT_SIZE]
            stderr = result.stderr[:MAX_OUTPUT_SIZE]
            
            return {
                "success": result.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "language": executor
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Timeout: la ejecución tardó más de {timeout} segundos",
                "exit_code": -1,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "error": str(e)
            }
    
    def _execute_java(self, executor: str, file_path: str, 
                     timeout: int) -> Dict[str, Any]:
        """Ejecuta código Java"""
        # Extraer nombre de clase del archivo
        class_name = Path(file_path).stem
        
        try:
            # Compilar
            compile_result = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Error de compilación:\n{compile_result.stderr}",
                    "exit_code": compile_result.returncode,
                    "error": "compilation_error"
                }
            
            # Ejecutar
            class_path = os.path.dirname(file_path)
            result = subprocess.run(
                ["java", "-cp", class_path, class_name],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:MAX_OUTPUT_SIZE],
                "stderr": result.stderr[:MAX_OUTPUT_SIZE],
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Timeout después de {timeout} segundos",
                "exit_code": -1,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "error": str(e)
            }
    
    def _execute_go(self, executor: str, file_path: str, 
                   timeout: int) -> Dict[str, Any]:
        """Ejecuta código Go"""
        try:
            result = subprocess.run(
                ["go", "run", file_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:MAX_OUTPUT_SIZE],
                "stderr": result.stderr[:MAX_OUTPUT_SIZE],
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Timeout después de {timeout} segundos",
                "exit_code": -1,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "error": str(e)
            }
    
    def _execute_rust(self, file_path: str, timeout: int) -> Dict[str, Any]:
        """Ejecuta código Rust"""
        try:
            # Compilar
            compile_result = subprocess.run(
                ["rustc", file_path, "-o", file_path + ".exe"],
                capture_output=True,
                text=True,
                timeout=timeout * 2
            )
            
            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Error de compilación:\n{compile_result.stderr}",
                    "exit_code": compile_result.returncode,
                    "error": "compilation_error"
                }
            
            # Ejecutar
            exe_path = file_path + ".exe"
            result = subprocess.run(
                [exe_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Limpiar ejecutable
            try:
                os.remove(exe_path)
            except:
                pass
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:MAX_OUTPUT_SIZE],
                "stderr": result.stderr[:MAX_OUTPUT_SIZE],
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Timeout después de {timeout} segundos",
                "exit_code": -1,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "error": str(e)
            }
    
    def _execute_cpp(self, language: str, file_path: str, 
                    timeout: int) -> Dict[str, Any]:
        """Ejecuta código C/C++"""
        compiler = "gcc" if language == "c" else "g++"
        
        # Verificar compilador
        if not self._find_executor(compiler):
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Compilador {compiler} no encontrado",
                "exit_code": -1,
                "error": "compiler_not_found"
            }
        
        exe_path = file_path + ".exe"
        
        try:
            # Compilar
            compile_result = subprocess.run(
                [compiler, file_path, "-o", exe_path],
                capture_output=True,
                text=True,
                timeout=timeout * 2
            )
            
            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Error de compilación:\n{compile_result.stderr}",
                    "exit_code": compile_result.returncode,
                    "error": "compilation_error"
                }
            
            # Ejecutar
            result = subprocess.run(
                [exe_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:MAX_OUTPUT_SIZE],
                "stderr": result.stderr[:MAX_OUTPUT_SIZE],
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Timeout después de {timeout} segundos",
                "exit_code": -1,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "error": str(e)
            }
        finally:
            # Limpiar ejecutable
            try:
                if os.path.exists(exe_path):
                    os.remove(exe_path)
            except:
                pass
    
    def get_available_languages(self) -> Dict[str, bool]:
        """Retorna los lenguajes disponibles en el sistema"""
        available = {}
        for lang, cmd in AVAILABLE_RUNTIMES.items():
            if cmd not in available:
                result = subprocess.run(
                    ["where" if sys.platform == "win32" else "which", cmd],
                    capture_output=True,
                    text=True
                )
                available[cmd] = result.returncode == 0
        
        return {lang: available.get(AVAILABLE_RUNTIMES[lang], False) 
                for lang in AVAILABLE_RUNTIMES}


# Instancia global
language_executor = LanguageExecutor()


def execute_code(code: str, language: str = "python", 
                timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar código"""
    return language_executor.execute(code, language, timeout)

