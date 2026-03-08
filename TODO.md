# Plan de Implementación: Asistente de Revisión de Código y Creación de Proyectos

## Información Recopilada
- **Sistema actual**: IA Local Vargas con memoria semántica, ejecución de código Python segura, procesamiento de documentos, búsqueda web
- **Technologias**: Ollama (LLM), SentenceTransformers (embeddings), Gradio (interfaz), SQLite (memoria)
- **Lenguajes soportados actualmente**: Solo Python (ejecución segura)

## Plan de Implementación

### 1. Nuevo Módulo: code_reviewer.py
Analiza código para detectar problemas y mejoras.

**Funcionalidades:**
- Revisión de seguridad (injection, XSS, etc.)
- Mejores prácticas (PEP8, SOLID, etc.)
- Análisis de complejidad
- Detección de code smells
- Sugerencias de optimización
- Revisión de documentación

### 2. Nuevo Módulo: project_creator.py
Crea proyectos completos en diferentes lenguajes.

**Lenguajes soportados:**
- Python (Django, Flask, FastAPI, CLI)
- JavaScript/TypeScript (React, Vue, Node.js)
- HTML/CSS (sitios estáticos)
- Java (Spring Boot, console)
- C# (.NET)
- Go
- Rust

**Estructura de proyectos:**
- Web apps
- APIs REST
- Software empresarial
- CLI tools
- Libraries/Paquetes

### 3. Nuevo Módulo: language_executor.py
Ejecuta código en múltiples lenguajes.

**Características:**
- Sandboxing seguro
- Soporte para: Python, Node.js, Go, Rust (si están instalados)
- Timeout configurable
- Captura de output/error

### 4. Expansión de Plugins
Nuevos comandos:
- `revisar:` - Revisar código
- `crear:` - Crear proyecto
- `ejecuta:` - Ejecutar código (ya existe, expandir)
- `generar:` - Generar código específico

### 5. Mejoras en app.py
- Integrar los nuevos módulos
- Nuevos comandos en el prompt builder
- Mejor detección de intents

## Archivos a Crear/Modificar
1. **Crear**: code_reviewer.py
2. **Crear**: project_creator.py
3. **Crear**: language_executor.py
4. **Modificar**: plugins.py - agregar nuevos plugins
5. **Modificar**: app.py - integrar nuevo sistema

## Pasos de Seguimiento
1. [ ] Crear code_reviewer.py con análisis de código
2. [ ] Crear project_creator.py con templates de proyectos
3. [ ] Crear language_executor.py para múltiples lenguajes
4. [ ] Actualizar plugins.py con nuevos plugins
5. [ ] Integrar en app.py
6. [ ] Probar funcionalidad

