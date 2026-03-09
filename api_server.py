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
from fastapi.responses import JSONResponse
import ollama
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports de módulos propios
from code_agent import run_python
from code_analyzer import CodeAnalyzer
from language_executor import LanguageExecutor
from project_creator import ProjectCreator

# Imports de ai_dev_system
try:
    from ai_dev_system.agents.orchestrator import create_orchestrator
    from ai_dev_system.editor.ai_commands import COMMANDS
    AI_DEV_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ai_dev_system no disponible: {e}")
    AI_DEV_SYSTEM_AVAILABLE = False

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

# Timeout para llamadas a Ollama (en segundos) - reducido para respuestas más rápidas
OLLAMA_TIMEOUT = 60  # 60 segundos timeout

# Thread pool for running Ollama calls
executor = ThreadPoolExecutor(max_workers=2)

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

# ============================================
# MODELOS ai_dev_system
# ============================================

class OrchestrateRequest(BaseModel):
    task: str
    workspace: Optional[str] = "workspace/projects"
    model: Optional[str] = MODEL
    max_iterations: int = 10

class CreateProjectRequest(BaseModel):
    description: str
    workspace: Optional[str] = "workspace/projects"
    language: str = "python"

class AgentCommandRequest(BaseModel):
    command: str
    code: str
    params: Optional[Dict[str, Any]] = None

class Response(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def call_ollama(prompt: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
    """Wrapper para llamar a Ollama con manejo de errores"""
    try:
        logger.info(f"Llamando a Ollama con modelo {MODEL}")
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )
        logger.info("Ollama respondió correctamente")
        return {"success": True, "response": response}
    except Exception as e:
        logger.error(f"Error en Ollama: {str(e)}")
        return {"success": False, "error": str(e)}

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
        "ai_dev_system": AI_DEV_SYSTEM_AVAILABLE,
        "endpoints": [
            "/ask",
            "/analyze",
            "/refactor",
            "/test",
            "/execute",
            "/generate",
            "/debug",
            "/optimize",
            "/orchestrate",
            "/create-project",
            "/agent/{command}",
            "/agents",
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
            "ai_dev_system": AI_DEV_SYSTEM_AVAILABLE,
            "available_models": [m.model for m in models.models] if hasattr(models, 'models') else []
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama": "disconnected",
            "ai_dev_system": AI_DEV_SYSTEM_AVAILABLE,
            "error": str(e)
        }

@app.post("/ask")
async def ask(request: AskRequest) -> Response:
    """
    Endpoint principal de chat con la IA
    """
    try:
        # Construir prompt con contexto
        prompt = request.prompt
        
        if request.context:
            context_str = "\n".join([f"{k}: {v}" for k, v in request.context.items()])
            prompt = f"""Contexto del proyecto:
{context_str}

Solicitud: {prompt}"""
        
        logger.info(f"Procesando solicitud /ask con prompt de {len(prompt)} caracteres")
        
        # Llamar a Ollama con timeout usando run_in_executor
        loop = asyncio.get_event_loop()
        
        try:
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    executor,
                    lambda: call_ollama(prompt, request.temperature, request.max_tokens)
                ),
                timeout=OLLAMA_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout esperando respuesta de Ollama ({OLLAMA_TIMEOUT}s)")
            return Response(
                success=False, 
                result=None, 
                error=f"Timeout: Ollama tardó más de {OLLAMA_TIMEOUT} segundos. El modelo puede estar cargando o el sistema tiene poca memoria."
            )
        
        if not response.get("success", False):
            error_msg = response.get("error", "Error desconocido")
            logger.error(f"Error de Ollama: {error_msg}")
            return Response(success=False, result=None, error=error_msg)
        
        result = response["response"]["message"]["content"]
        logger.info(f"Respuesta recibida, {len(result)} caracteres")
        return Response(success=True, result=result)
    
    except asyncio.TimeoutError:
        return Response(success=False, result=None, error=f"Timeout: La solicitud tardó más de {OLLAMA_TIMEOUT} segundos")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error en /ask: {error_msg}")
        # Detectar si es un error de cancelación
        if "cancel" in error_msg.lower() or "abort" in error_msg.lower():
            return Response(success=False, result=None, error="La solicitud fue cancelada. Por favor intenta de nuevo.")
        return Response(success=False, result=None, error=error_msg)

@app.post("/analyze")
async def analyze_code(request: AnalyzeRequest) -> Response:
    """
    Analiza código para detectar problemas, vulnerabilidades y sugerencias
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
# ENDPOINTS ai_dev_system
# ============================================

@app.post("/orchestrate")
async def orchestrate_task(request: OrchestrateRequest) -> Response:
    """
    Ejecuta una tarea compleja usando el orquestador de ai_dev_system
    """
    if not AI_DEV_SYSTEM_AVAILABLE:
        return Response(
            success=False, 
            result=None, 
            error="ai_dev_system no está disponible. Asegúrate de que las dependencias estén instaladas."
        )
    
    try:
        logger.info(f"Orquestando tarea: {request.task}")
        
        # Crear orquestador
        orchestrator = create_orchestrator(
            model=request.model,
            workspace=request.workspace
        )
        
        # Ejecutar tarea
        result = orchestrator.execute(
            task=request.task,
            workspace=request.workspace
        )
        
        logger.info(f"Orquestación completada: {result.get('status')}")
        return Response(success=True, result=result)
    
    except Exception as e:
        logger.error(f"Error en orquestación: {str(e)}")
        return Response(success=False, result=None, error=str(e))

@app.post("/create-project")
async def create_project(request: CreateProjectRequest) -> Response:
    """
    Crea un proyecto completo usando ai_dev_system
    """
    if not AI_DEV_SYSTEM_AVAILABLE:
        return Response(
            success=False, 
            result=None, 
            error="ai_dev_system no está disponible."
        )
    
    try:
        logger.info(f"Creando proyecto: {request.description}")
        
        # Usar el orquestador para crear el proyecto
        orchestrator = create_orchestrator(
            model=MODEL,
            workspace=request.workspace
        )
        
        result = orchestrator.execute(
            task=f"Create a {request.language} project: {request.description}",
            workspace=request.workspace
        )
        
        return Response(success=True, result=result)
    
    except Exception as e:
        logger.error(f"Error creando proyecto: {str(e)}")
        return Response(success=False, result=None, error=str(e))

@app.post("/agent/{agent_command}")
async def execute_agent_command(
    agent_command: str,
    request: AgentCommandRequest
) -> Response:
    """
    Ejecuta un comando de agente específico
    """
    if not AI_DEV_SYSTEM_AVAILABLE:
        return Response(
            success=False, 
            result=None, 
            error="ai_dev_system no está disponible."
        )
    
    try:
        from ai_dev_system.editor.ai_commands import execute_command
        
        logger.info(f"Ejecutando comando de agente: {agent_command}")
        
        result = execute_command(
            command=agent_command,
            code=request.code,
            **(request.params or {})
        )
        
        return Response(success=True, result=result)
    
    except Exception as e:
        logger.error(f"Error en comando de agente: {str(e)}")
        return Response(success=False, result=None, error=str(e))

@app.get("/agents")
async def list_agents() -> Response:
    """
    Lista los agentes disponibles en ai_dev_system
    """
    if not AI_DEV_SYSTEM_AVAILABLE:
        return Response(
            success=False, 
            result=None, 
            error="ai_dev_system no está disponible."
        )
    
    try:
        from ai_dev_system.editor.ai_commands import COMMANDS
        
        return Response(success=True, result={
            "agents": list(COMMANDS.keys()),
            "count": len(COMMANDS)
        })
    
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
    print(f"ai_dev_system: {'Disponible' if AI_DEV_SYSTEM_AVAILABLE else 'No disponible'}")
    print(f"Timeout de Ollama: {OLLAMA_TIMEOUT} segundos")
    print("Endpoints disponibles:")
    print("  - /ask          : Chat con la IA")
    print("  - /analyze      : Analizar codigo")
    print("  - /refactor     : Refactorizar codigo")
    print("  - /test         : Generar tests")
    print("  - /execute      : Ejecutar codigo")
    print("  - /generate     : Generar codigo")
    print("  - /debug        : Depurar codigo")
    print("  - /optimize     : Optimizar codigo")
    if AI_DEV_SYSTEM_AVAILABLE:
        print("  - /orchestrate  : Orquestar tarea compleja")
        print("  - /create-project: Crear proyecto completo")
        print("  - /agent/{cmd}  : Ejecutar comando de agente")
        print("  - /agents       : Listar agentes disponibles")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)

