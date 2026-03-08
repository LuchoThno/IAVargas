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

