"""
IA Local Vargas - FastAPI Server
=================================
API REST para integración con IDEs (VSCode, IntelliJ)
Proporciona endpoints para análisis, generación y ejecución de código

Endpoints:
- /ask - Chat con la IA
- /analyze - Analizar código
- /refactor - Refactorizar código
- /test - Generar tests
- /execute - Ejecutar código
- /generate - Generar código
- /debug - Analizar y encontrar errores
- /optimize - Optimizar código
"""

import os
import sys
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import ollama

# Imports de módulos propios
from code_agent import run_python
from code_analyzer import CodeAnalyzer
from language_executor import LanguageExecutor
from project_creator import ProjectCreator

# ============================================
# CONFIGURACIÓN
# ============================================

app = FastAPI(
    title="IA Local Vargas API",
    description="API local para asistencia de programación con IA",
    version="1.0.0"
)

# CORS para permitir conexiones desde IDEs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = os.getenv("OLLAMA_MODEL", "llama3")
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048

# Instancias de servicios
code_analyzer = CodeAnalyzer()
language_executor = LanguageExecutor()
project_creator = ProjectCreator()

# ============================================
# MODELOS Pydantic
# ============================================

class AskRequest(BaseModel):
    prompt: str
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    context: Optional[Dict[str, Any]] = None

class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"
    include_security: bool = True
    include_complexity: bool = True

class RefactorRequest(BaseModel):
    code: str
    language: str = "python"
    style: str = "default"
    goal: Optional[str] = None

class TestRequest(BaseModel):
    code: str
    language: str = "python"
    framework: Optional[str] = None
    test_count: int = 3

class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30

class GenerateRequest(BaseModel):
    description: str
    language: str = "python"
    project_type: Optional[str] = None

class DebugRequest(BaseModel):
    code: str
    language: str = "python"
    error_message: Optional[str] = None

class OptimizeRequest(BaseModel):
    code: str
    language: str = "python"
    focus: str = "performance"

class Response(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None

# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def root():
    """Información básica de la API"""
    return {
        "name": "IA Local Vargas API",
        "version": "1.0.0",
        "status": "running",
        "model": MODEL,
        "endpoints": [
            "/ask",
            "/analyze",
            "/refactor",
            "/test",
            "/execute",
            "/generate",
            "/debug",
            "/optimize",
            "/health"
        ]
    }

@app.get("/health")
def health_check():
    """Verifica el estado de la API"""
    try:
        # Verificar Ollama
        models = ollama.list()
        return {
            "status": "healthy",
            "ollama": "connected",
            "model": MODEL,
            "available_models": [m.model for m in models.models] if hasattr(models, 'models') else []
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama": "disconnected",
            "error": str(e)
        }

@app.post("/ask")
async def ask(request: AskRequest) -> Response:
    """
    Endpoint principal de chat con la IA
    
    Args:
        prompt: La pregunta o solicitud del usuario
        temperature: Temperatura para la generación (0-1)
        max_tokens: Máximo de tokens a generar
        context: Contexto adicional (archivo actual, proyecto, etc.)
    """
    try:
        # Construir prompt con contexto
        prompt = request.prompt
        
        if request.context:
            context_str = "\n".join([f"{k}: {v}" for k, v in request.context.items()])
            prompt = f"""Contexto del proyecto:
{context_str}

Solicitud: {prompt}"""
        
        # Llamar a Ollama
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        )
        
        result = response["message"]["content"]
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

@app.post("/analyze")
async def analyze_code(request: AnalyzeRequest) -> Response:
    """
    Analiza código para detectar problemas, vulnerabilidades y sugerencias
    
    Args:
        code: Código a analizar
        language: Lenguaje de programación
        include_security: Incluir análisis de seguridad
        include_complexity: Incluir análisis de complejidad
    """
    try:
        result = code_analyzer.analyze(
            code=request.code,
            language=request.language,
            check_security=request.include_security,
            check_complexity=request.include_complexity
        )
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

@app.post("/refactor")
async def refactor_code(request: RefactorRequest) -> Response:
    """
    Refactoriza código según el objetivo especificado
    
    Args:
        code: Código a refactorizar
        language: Lenguaje de programación
        style: Estilo de refactorización (default, functional, oop)
        goal: Objetivo específico (legibility, performance, etc.)
    """
    try:
        result = code_analyzer.refactor(
            code=request.code,
            language=request.language,
            style=request.style,
            goal=request.goal
        )
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

@app.post("/test")
async def generate_tests(request: TestRequest) -> Response:
    """
    Genera tests unitarios para el código proporcionado
    
    Args:
        code: Código para generar tests
        language: Lenguaje de programación
        framework: Framework de testing (pytest, unittest, etc.)
        test_count: Número de tests a generar
    """
    try:
        result = code_analyzer.generate_tests(
            code=request.code,
            language=request.language,
            framework=request.framework,
            count=request.test_count
        )
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

@app.post("/execute")
async def execute_code(request: ExecuteRequest) -> Response:
    """
    Ejecuta código de forma segura
    
    Args:
        code: Código a ejecutar
        language: Lenguaje de programación
        timeout: Timeout en segundos
    """
    try:
        result = language_executor.execute(
            code=request.code,
            language=request.language,
            timeout=request.timeout
        )
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

@app.post("/generate")
async def generate_code(request: GenerateRequest) -> Response:
    """
    Genera código basado en una descripción
    
    Args:
        description: Descripción de lo que se quiere generar
        language: Lenguaje de programación
        project_type: Tipo de proyecto (web, api, cli, etc.)
    """
    try:
        result = project_creator.generate(
            description=request.description,
            language=request.language,
            project_type=request.project_type
        )
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

@app.post("/debug")
async def debug_code(request: DebugRequest) -> Response:
    """
    Analiza código para encontrar y corregir errores
    
    Args:
        code: Código con errores
        language: Lenguaje de programación
        error_message: Mensaje de error opcional
    """
    try:
        result = code_analyzer.debug(
            code=request.code,
            language=request.language,
            error_message=request.error_message
        )
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

@app.post("/optimize")
async def optimize_code(request: OptimizeRequest) -> Response:
    """
    Optimiza código para mejor rendimiento
    
    Args:
        code: Código a optimizar
        language: Lenguaje de programación
        focus: Área de enfoque (performance, memory, readability)
    """
    try:
        result = code_analyzer.optimize(
            code=request.code,
            language=request.language,
            focus=request.focus
        )
        return Response(success=True, result=result)
    
    except Exception as e:
        return Response(success=False, result=None, error=str(e))

# ============================================
# EJECUCIÓN DEL SERVIDOR
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    PORT = int(os.getenv("API_PORT", "8000"))
    
    print(f"Iniciando IA Local Vargas API en puerto {PORT}...")
    print(f"Modelo: {MODEL}")
    print("Endpoints disponibles:")
    print("  - /ask        : Chat con la IA")
    print("  - /analyze    : Analizar código")
    print("  - /refactor   : Refactorizar código")
    print("  - /test       : Generar tests")
    print("  - /execute    : Ejecutar código")
    print("  - /generate   : Generar código")
    print("  - /debug      : Depurar código")
    print("  - /optimize   : Optimizar código")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)

