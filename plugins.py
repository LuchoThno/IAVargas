"""
Plugin System - Arquitectura de Extensiones
===========================================
IA Local Vargas - Sistema de Plugins
Permite agregar funcionalidades adicionales mediante plugins
"""

import re
import math
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime


class Plugin:
    """Clase base para plugins"""
    
    name: str = "Base Plugin"
    description: str = "Plugin base"
    commands: List[str] = []
    
    def execute(self, args: str) -> str:
        """Ejecuta el plugin con los argumentos dados"""
        raise NotImplementedError
    
    def help(self) -> str:
        """Retorna la ayuda del plugin"""
        return f"{self.name}: {self.description}"


class CalculatorPlugin(Plugin):
    """Plugin de calculadora"""
    
    name = "Calculadora"
    description = "Realiza cálculos matemáticos"
    commands = ["calc:", "calcula:", "math:"]
    
    def execute(self, args: str) -> str:
        """Ejecuta cálculos matemáticos"""
        if not args.strip():
            return "Uso: calc: 2+2, calc: sqrt(16), calc: sin(0)"
        
        try:
            # Reemplazar funciones matemáticas comunes
            expr = args.strip()
            expr = re.sub(r'\bsqrt\b', 'math.sqrt', expr)
            expr = re.sub(r'\bsin\b', 'math.sin', expr)
            expr = re.sub(r'\bcos\b', 'math.cos', expr)
            expr = re.sub(r'\btan\b', 'math.tan', expr)
            expr = re.sub(r'\blog\b', 'math.log', expr)
            expr = re.sub(r'\bexp\b', 'math.exp', expr)
            expr = re.sub(r'\bpi\b', 'math.pi', expr)
            expr = re.sub(r'\bpow\b', 'math.pow', expr)
            
            # Evaluar expresión
            result = eval(expr, {"__builtins__": {"math": math}}, {"math": math})
            return f"Resultado: {result}"
        except Exception as e:
            return f"Error en cálculo: {str(e)}"
    
    def help(self) -> str:
        return """**Calculadora** - Realiza cálculos matemáticos
Comandos: `calc:`, `calcula:`, `math:`
Ejemplos:
- `calc: 2+2*3`
- `calc: sqrt(16)`
- `calc: sin(0) + cos(0)`"""


class DateTimePlugin(Plugin):
    """Plugin de fecha y hora"""
    
    name = "Fecha/Hora"
    description = "Muestra fecha y hora actual"
    commands = ["hora", "fecha", "datetime", "ahora"]
    
    def execute(self, args: str) -> str:
        """Retorna fecha y hora actual"""
        now = datetime.now()
        return f"""**Fecha y Hora Actual:**
- Fecha: {now.strftime('%d/%m/%Y')}
- Hora: {now.strftime('%H:%M:%S')}
- Día: {now.strftime('%A')}
- Semana: {now.isocalendar()[1]}"""
    
    def help(self) -> str:
        return """**Fecha/Hora** - Muestra la fecha y hora actual
Comandos: `hora`, `fecha`, `ahora`"""


class NotePlugin(Plugin):
    """Plugin para tomar notas"""
    
    name = "Notas"
    description = "Guarda y recupera notas"
    commands = ["nota:", "note:"]
    
    def __init__(self):
        self.notes: Dict[str, str] = {}
    
    def execute(self, args: str) -> str:
        """Guarda o recupera notas"""
        if not args.strip():
            if not self.notes:
                return "No hay notas guardadas"
            result = "**Notas guardadas:**\n"
            for key, value in self.notes.items():
                result += f"- {key}: {value}\n"
            return result
        
        # Formato: "titulo: contenido" o "ver: titulo"
        if args.startswith("ver:") or args.startswith("get:"):
            key = args.split(":", 1)[1].strip()
            if key in self.notes:
                return f"**Nota [{key}]:**\n{self.notes[key]}"
            return f"Nota '{key}' no encontrada"
        
        if ":" in args:
            key, content = args.split(":", 1)
            self.notes[key.strip()] = content.strip()
            return f"✅ Nota guardada: '{key.strip()}'"
        
        return "Uso: nota: titulo: contenido o nota: ver: titulo"
    
    def help(self) -> str:
        return """**Notas** - Guarda y recupera notas
Comandos: `nota:`
Ejemplos:
- `nota:-recordatorio: Comprar leche` - Guarda nota
- `nota: ver: recordatorio` - Recupera nota
- `nota:` - Lista todas las notas"""


class TodoPlugin(Plugin):
    """Plugin de lista de tareas"""
    
    name = "Tareas"
    description = "Gestiona lista de tareas"
    commands = ["tarea:", "todo:", "task:"]
    
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
    
    def execute(self, args: str) -> str:
        """Gestiona tareas"""
        args = args.strip().lower()
        
        if not args or args == "listar" or args == "ver":
            if not self.tasks:
                return "No hay tareas pendientes"
            result = "**Tareas pendientes:**\n"
            for i, task in enumerate(self.tasks, 1):
                status = "✅" if task.get("done") else "⬜"
                result += f"{i}. {status} {task['text']}\n"
            return result
        
        if args.startswith("add:") or args.startswith("agregar:") or args.startswith("+"):
            task_text = args.split(":", 1)[1].strip() if ":" in args else args[1:].strip()
            self.tasks.append({"text": task_text, "done": False})
            return f"✅ Tarea agregada: '{task_text}'"
        
        if args.startswith("done:") or args.startswith("completar:") or args.startswith("x:"):
            try:
                idx = int(args.split(":", 1)[1].strip()) - 1
                if 0 <= idx < len(self.tasks):
                    self.tasks[idx]["done"] = True
                    return f"✅ Tarea completada: '{self.tasks[idx]['text']}'"
                return "Índice de tarea inválido"
            except ValueError:
                return "Uso: tarea: done: 1"
        
        if args.startswith("del:") or args.startswith("borrar:") or args.startswith("-"):
            try:
                idx = int(args.split(":", 1)[1].strip()) - 1
                if 0 <= idx < len(self.tasks):
                    removed = self.tasks.pop(idx)
                    return f"🗑️ Tarea eliminada: '{removed['text']}'"
                return "Índice de tarea inválido"
            except ValueError:
                return "Uso: tarea: del: 1"
        
        return self.help()
    
    def help(self) -> str:
        return """**Tareas** - Gestiona lista de tareas
Comandos: `tarea:`, `todo:`
Ejemplos:
- `tarea: + Comprar leche` - Agregar tarea
- `tarea: ver` - Ver todas las tareas
- `tarea: done: 1` - Completar tarea
- `tarea: del: 1` - Eliminar tarea"""


class HelpPlugin(Plugin):
    """Plugin de ayuda general"""
    
    name = "Ayuda"
    description = "Muestra información de ayuda"
    commands = ["ayuda", "help", "comandos"]
    
    def execute(self, args: str) -> str:
        """Muestra ayuda"""
        return """**Comandos disponibles:**

**Sistema:**
- `ejecuta: codigo` - Ejecutar código Python
- `busca: query` - Búsqueda web
- `ayuda` - Mostrar ayuda

**Análisis de Código:**
- `/analyze` - Analizar código
- `/refactor` - Refactorizar código
- `/test` - Generar tests
- `/debug` - Depurar código
- `/optimize` - Optimizar código
- `/generate` - Generar código

**Plugins:**
- `calc:` - Calculadora matemática
- `hora` / `fecha` - Fecha y hora actual
- `nota:` - Guardar y recuperar notas
- `tarea:` - Gestionar tareas

**Configuración:**
- Temperature: Controla creatividad (0-1)
- Max Tokens: Longitud máxima de respuesta"""
    
    def help(self) -> str:
        return "**Ayuda** - Muestra todos los comandos disponibles"


class CodeAnalyzePlugin(Plugin):
    """Plugin para análisis de código"""
    
    name = "Analizar Código"
    description = "Analiza código para detectar problemas y sugerencias"
    commands = ["/analyze", "analiza:", "revisar:"]
    
    def __init__(self):
        self.analyzer = None
    
    def execute(self, args: str) -> str:
        """Analiza código"""
        if not args.strip():
            return "Uso: /analyze [código Python] o analiza: [código]"
        
        # Intentar importar el analizador
        try:
            from code_analyzer import CodeAnalyzer
            if not self.analyzer:
                self.analyzer = CodeAnalyzer()
            
            result = self.analyzer.analyze(args, "python")
            
            output = f"**Análisis de Código**\n\n"
            output += f"Líneas: {result.get('lines', 0)}\n"
            output += f"Puntuación: {result.get('score', 0)}/100\n\n"
            
            if result.get("security_issues"):
                output += "**⚠️ Problemas de Seguridad:**\n"
                for issue in result["security_issues"]:
                    output += f"- {issue['message']}\n"
                output += "\n"
            
            if result.get("complexity"):
                comp = result["complexity"]
                output += "**📊 Complejidad:**\n"
                output += f"- Complejidad ciclomática: {comp.get('cyclomatic', 0)}\n"
                output += f"- Funciones: {comp.get('functions', 0)}\n"
                output += f"- Clases: {comp.get('classes', 0)}\n\n"
            
            if result.get("suggestions"):
                output += "**💡 Sugerencias:**\n"
                for suggestion in result["suggestions"][:5]:
                    output += f"- {suggestion}\n"
            
            return output
        except ImportError:
            return "Error: code_analyzer no está disponible. Instala las dependencias."
        except Exception as e:
            return f"Error al analizar: {str(e)}"
    
    def help(self) -> str:
        return """**Analizar Código** - Analiza código para detectar problemas
Comandos: `/analyze`, `analiza:`, `revisar:`
Ejemplo:
- `/analyze def hola(): print("hola")`"""


class CodeRefactorPlugin(Plugin):
    """Plugin para refactorizar código"""
    
    name = "Refactorizar"
    description = "Refactoriza código para mejorarlo"
    commands = ["/refactor", "refactor:"]
    
    def __init__(self):
        self.analyzer = None
    
    def execute(self, args: str) -> str:
        """Refactoriza código"""
        if not args.strip():
            return "Uso: /refactor [código Python]"
        
        try:
            from code_analyzer import CodeAnalyzer
            if not self.analyzer:
                self.analyzer = CodeAnalyzer()
            
            result = self.analyzer.refactor(args, "python")
            
            if "error" in result:
                return f"Error: {result['error']}"
            
            output = "**Código Refactorizado:**\n\n"
            output += "```python\n"
            output += result.get("refactored_code", "") + "\n"
            output += "```\n\n"
            
            return output
        except ImportError:
            return "Error: code_analyzer no está disponible."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def help(self) -> str:
        return """**Refactorizar** - Refactoriza código
Comandos: `/refactor`, `refactor:`
Ejemplo:
- `/refactor def hola(): print("hola")`"""


class CodeTestPlugin(Plugin):
    """Plugin para generar tests"""
    
    name = "Generar Tests"
    description = "Genera tests unitarios para el código"
    commands = ["/test", "test:", "genera test:"]
    
    def __init__(self):
        self.analyzer = None
    
    def execute(self, args: str) -> str:
        """Genera tests"""
        if not args.strip():
            return "Uso: /test [código Python]"
        
        try:
            from code_analyzer import CodeAnalyzer
            if not self.analyzer:
                self.analyzer = CodeAnalyzer()
            
            result = self.analyzer.generate_tests(args, "python", "pytest")
            
            if "error" in result:
                return f"Error: {result['error']}"
            
            output = f"**Tests Generados ({result.get('framework', 'pytest')}):**\n\n"
            output += "```python\n"
            output += result.get("tests", "") + "\n"
            output += "```\n"
            
            return output
        except ImportError:
            return "Error: code_analyzer no está disponible."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def help(self) -> str:
        return """**Generar Tests** - Crea tests unitarios
Comandos: `/test`, `test:`
Ejemplo:
- `/test def suma(a, b): return a + b`"""


class CodeDebugPlugin(Plugin):
    """Plugin para depurar código"""
    
    name = "Depurar"
    description = "Encuentra y corrige errores en el código"
    commands = ["/debug", "debug:", "arreglar:"]
    
    def __init__(self):
        self.analyzer = None
    
    def execute(self, args: str) -> str:
        """Depura código"""
        if not args.strip():
            return "Uso: /debug [código Python]"
        
        try:
            from code_analyzer import CodeAnalyzer
            if not self.analyzer:
                self.analyzer = CodeAnalyzer()
            
            result = self.analyzer.debug(args, "python")
            
            if "error" in result:
                return f"Error: {result['error']}"
            
            output = "**Código Corregido:**\n\n"
            output += "```python\n"
            output += result.get("fixed_code", "") + "\n"
            output += "```\n"
            
            return output
        except ImportError:
            return "Error: code_analyzer no está disponible."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def help(self) -> str:
        return """**Depurar** - Encuentra y corrige errores
Comandos: `/debug`, `debug:`
Ejemplo:
- `/debug print("hola"`"""


class CodeOptimizePlugin(Plugin):
    """Plugin para optimizar código"""
    
    name = "Optimizar"
    description = "Optimiza código para mejor rendimiento"
    commands = ["/optimize", "optimizar:", "mejora:"]
    
    def __init__(self):
        self.analyzer = None
    
    def execute(self, args: str) -> str:
        """Optimiza código"""
        if not args.strip():
            return "Uso: /optimize [código Python]"
        
        try:
            from code_analyzer import CodeAnalyzer
            if not self.analyzer:
                self.analyzer = CodeAnalyzer()
            
            result = self.analyzer.optimize(args, "python")
            
            if "error" in result:
                return f"Error: {result['error']}"
            
            output = "**Código Optimizado:**\n\n"
            output += "```python\n"
            output += result.get("optimized_code", "") + "\n"
            output += "```\n"
            
            return output
        except ImportError:
            return "Error: code_analyzer no está disponible."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def help(self) -> str:
        return """**Optimizar** - Optimiza código para mejor rendimiento
Comandos: `/optimize`, `optimizar:`
Ejemplo:
- `/optimize for i in range(1000): print(i)`"""


class CodeGeneratePlugin(Plugin):
    """Plugin para generar código"""
    
    name = "Generar Código"
    description = "Genera código basado en descripción"
    commands = ["/generate", "genera:", "crear:"]
    
    def __init__(self):
        self.creator = None
    
    def execute(self, args: str) -> str:
        """Genera código"""
        if not args.strip():
            return "Uso: /generate [descripción del código]"
        
        try:
            from project_creator import ProjectCreator
            if not self.creator:
                self.creator = ProjectCreator()
            
            result = self.creator.generate(args, "python")
            
            if not result.get("success"):
                return f"Error: {result.get('error', 'Unknown error')}"
            
            output = "**Código Generado:**\n\n"
            
            files = result.get("files", {})
            if files:
                for file_name in list(files.keys())[:3]:
                    output += f"### {file_name}\n"
                    output += "```python\n"
                    output += files[file_name][:500] + "\n"
                    output += "```\n\n"
            
            return output
        except ImportError:
            return "Error: project_creator no está disponible."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def help(self) -> str:
        return """**Generar Código** - Crea código desde cero
Comandos: `/generate`, `genera:`
Ejemplo:
- `/generate función que calcule factorial`"""


class ExecuteMultiPlugin(Plugin):
    """Plugin para ejecutar múltiples lenguajes"""
    
    name = "Ejecutar Código"
    description = "Ejecuta código en múltiples lenguajes"
    commands = ["ejecuta:", "run:", "ejecutar:"]
    
    def __init__(self):
        self.executor = None
    
    def execute(self, args: str) -> str:
        """Ejecuta código"""
        if not args.strip():
            return "Uso: ejecuta: [código] (lenguaje: python)"
        
        try:
            from language_executor import LanguageExecutor
            if not self.executor:
                self.executor = LanguageExecutor()
            
            # Detectar lenguaje
            language = "python"
            code = args
            
            # Si hay prefijo de lenguaje
            if args.lower().startswith("python:"):
                code = args[7:]
                language = "python"
            elif args.lower().startswith("js:"):
                code = args[3:]
                language = "javascript"
            elif args.lower().startswith("node:"):
                code = args[5:]
                language = "javascript"
            
            result = self.executor.execute(code, language, timeout=10)
            
            output = f"**Ejecución ({language}):**\n\n"
            
            if result.get("success"):
                output += f"✅ **Salida:**\n{result.get('stdout', 'Sin salida')}\n"
            else:
                output += f"❌ **Error:**\n{result.get('stderr', result.get('error', 'Unknown error'))}\n"
            
            return output
        except ImportError:
            return "Error: language_executor no está disponible."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def help(self) -> str:
        return """**Ejecutar Código** - Ejecuta código en múltiples lenguajes
Comandos: `ejecuta:`, `run:`
Ejemplos:
- `ejecuta: print("hola")`
- `ejecuta: js: console.log("hola")`"""


class PluginManager:
    """Gestor de plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Registra los plugins por defecto"""
        self.register(CalculatorPlugin())
        self.register(DateTimePlugin())
        self.register(NotePlugin())
        self.register(TodoPlugin())
        self.register(HelpPlugin())
        # Nuevos plugins de código
        self.register(CodeAnalyzePlugin())
        self.register(CodeRefactorPlugin())
        self.register(CodeTestPlugin())
        self.register(CodeDebugPlugin())
        self.register(CodeOptimizePlugin())
        self.register(CodeGeneratePlugin())
        self.register(ExecuteMultiPlugin())
    
    def register(self, plugin: Plugin):
        """Registra un nuevo plugin"""
        for cmd in plugin.commands:
            self.plugins[cmd] = plugin
    
    def unregister(self, command: str):
        """Elimina un plugin"""
        if command in self.plugins:
            del self.plugins[command]
    
    def get_plugin(self, command: str) -> Optional[Plugin]:
        """Obtiene un plugin por comando"""
        return self.plugins.get(command)
    
    def process(self, message: str) -> Optional[str]:
        """Procesa un mensaje y retorna respuesta si hay match"""
        message_lower = message.lower().strip()
        
        # Buscar plugin por prefijo
        for cmd, plugin in self.plugins.items():
            if message_lower.startswith(cmd):
                args = message[len(cmd):].strip()
                return plugin.execute(args)
        
        # Buscar por palabra clave (para help, hora, fecha)
        for cmd, plugin in self.plugins.items():
            if message_lower == cmd or message_lower.startswith(cmd + " "):
                args = message[len(cmd):].strip()
                return plugin.execute(args)
        
        return None
    
    def list_plugins(self) -> str:
        """Lista todos los plugins disponibles"""
        result = "**Plugins disponibles:**\n"
        for plugin in set(self.plugins.values()):
            result += f"- {plugin.help()}\n\n"
        return result


# Instancia global del gestor de plugins
plugin_manager = PluginManager()


def process_plugin(message: str) -> Optional[str]:
    """Función de conveniencia para procesar plugins"""
    return plugin_manager.process(message)

