"""
Secure Python Code Execution Agent
=================================

Mejoras:
- Sandbox con proceso aislado
- Análisis AST seguro
- Timeout real
- Límite de memoria
- Import controlado
- Captura de stdout/stderr
"""

import ast
import io
import sys
import traceback
import multiprocessing
import platform

# Resource module is Unix-only, so we handle it conditionally
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

from typing import Tuple, Dict, Any, Optional

DEFAULT_TIMEOUT = 5
MEMORY_LIMIT_MB = 128

ALLOWED_MODULES = {
    "math",
    "random",
    "statistics",
    "datetime",
    "time",
    "json",
    "re",
    "collections",
    "itertools",
    "functools",
    "operator",
    "string",
}

BLOCKED_NAMES = {
    "eval",
    "exec",
    "compile",
    "open",
    "__import__",
    "input",
    "globals",
    "locals",
    "vars",
    "dir",
}

BLOCKED_ATTRS = {
    "__globals__",
    "__code__",
    "__closure__",
    "__subclasses__",
    "__bases__",
}


class SecurityVisitor(ast.NodeVisitor):
    """
    Analiza el AST para detectar código peligroso
    """

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split(".")[0] not in ALLOWED_MODULES:
                raise SecurityError(f"Import no permitido: {alias.name}")

    def visit_ImportFrom(self, node):
        if node.module and node.module.split(".")[0] not in ALLOWED_MODULES:
            raise SecurityError(f"Import no permitido: {node.module}")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_NAMES:
                raise SecurityError(f"Llamada bloqueada: {node.func.id}")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr in BLOCKED_ATTRS:
            raise SecurityError(f"Atributo bloqueado: {node.attr}")
        self.generic_visit(node)


class SecurityError(Exception):
    pass


def _limit_resources():
    """
    Limita memoria del proceso (solo disponible en Unix)
    En Windows, la limitación de memoria se omite pero el aislamiento
    de proceso proporciona protección adicional.
    """
    if HAS_RESOURCE:
        memory_bytes = MEMORY_LIMIT_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Import seguro
    """
    if name.split(".")[0] not in ALLOWED_MODULES:
        raise ImportError(f"Import bloqueado: {name}")
    return __import__(name, globals, locals, fromlist, level)


def _safe_builtins():
    """
    Builtins permitidos
    """

    safe = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "pow": pow,
        "print": print,
        "range": range,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    }

    safe["__import__"] = _safe_import

    return safe


def _execute(code: str, queue):
    """
    Ejecuta el código dentro de un proceso sandbox
    """

    _limit_resources()

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    sys.stdout = stdout_capture
    sys.stderr = stderr_capture

    safe_globals = {
        "__builtins__": _safe_builtins(),
    }

    try:
        compiled = compile(code, "<agent>", "exec")
        exec(compiled, safe_globals)

        queue.put(
            {
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "error": None,
            }
        )

    except Exception:
        queue.put(
            {
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "error": traceback.format_exc(),
            }
        )


class SecureExecution:
    """
    Motor seguro de ejecución
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def validate(self, code: str):
        """
        Valida el código usando AST
        """
        tree = ast.parse(code)
        SecurityVisitor().visit(tree)

    def run(self, code: str) -> Tuple[str, str, Optional[str]]:

        try:
            self.validate(code)
        except SecurityError as e:
            return "", "", f"⚠️ Seguridad: {str(e)}"
        except Exception as e:
            return "", "", f"Error de parsing: {str(e)}"

        queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=_execute, args=(code, queue))

        process.start()
        process.join(self.timeout)

        if process.is_alive():
            process.terminate()
            return "", "", "⏱️ Timeout: ejecución demasiado larga"

        if queue.empty():
            return "", "", "Error interno"

        result = queue.get()

        return result["stdout"], result["stderr"], result["error"]


def run_python(code: str) -> str:
    """
    API principal para el agente
    """

    code = code.strip()

    prefixes = ["ejecuta:", "run:", "python:", "code:"]
    for p in prefixes:
        if code.lower().startswith(p):
            code = code[len(p):].strip()

    executor = SecureExecution()

    stdout, stderr, error = executor.run(code)

    output = []

    if stdout:
        output.append(f"📤 **Salida:**\n{stdout}")

    if stderr:
        output.append(f"⚠️ **Stderr:**\n{stderr}")

    if error:
        output.append(f"❌ **Error:**\n{error}")

    if not output:
        return "✅ Código ejecutado correctamente"

    return "\n\n".join(output)