# IA Local Vargas - IntelliJ IDEA Plugin

Plugin para IntelliJ IDEA que integra el asistente de IA local.

## Características

- 🤖 **Chat con IA**: Pregunta a tu asistente de IA local
- 📊 **Análisis de Código**: Detecta problemas de seguridad y complejidad
- 🔄 **Refactorización**: Mejora tu código automáticamente
- 🧪 **Generación de Tests**: Crea tests unitarios
- 🐛 **Depuración**: Encuentra y corrige errores
- ⚡ **Optimización**: Mejora el rendimiento
- 💻 **Ejecución**: Ejecuta código directamente
- 📖 **Explicación**: Explica código seleccionado

## Requisitos

- [IntelliJ IDEA](https://www.jetbrains.com/idea/) 2023.3+
- [Ollama](https://ollama.ai/) instalado y ejecutándose
- API de IA Local Vargas ejecutándose (`python api_server.py`)

## Instalación

### Opción 1: Pre-built JAR

1. Descarga el archivo `.jar` del plugin
2. Ve a `Settings > Plugins`
3. Haz clic en el engranaje > "Install Plugin from Disk"
4. Selecciona el archivo descargado

### Opción 2: Desarrollo local (Windows)

```batch
cd intellij_plugin
call build.bat
```

O manualmente, usa Gradle directamente o IntelliJ IDEA para importar el proyecto como Gradle.

### Opción 3: Desarrollo local (Linux/Mac)

```bash
# Clonar el repositorio
git clone <repo-url>
cd IAVargas/intellij_plugin

# Instalar dependencias y construir
gradle buildPlugin

# Instalar el plugin desde el JAR generado
# en build/distributions/
```

## Configuración

Ve a `Settings > Tools > IA Local Vargas`:

| Opción | Descripción | Default |
|--------|-------------|---------|
| API URL | URL de la API | `http://localhost:8000` |
| Modelo | Modelo de Ollama | `llama3` |
| Temperature | Creatividad (0-1) | `0.7` |
| Max Tokens | Máx. tokens | `2048` |

## Uso

### Desde el Editor

1. Selecciona código en el editor
2. Haz clic derecho > menú "IA Vargas"
3. Elige la acción deseada

### Desde la Barra de Herramientas

- Barra de herramientas de ejecución

### Acciones Disponibles

| Acción | Descripción |
|--------|-------------|
| Analizar Código | Analiza el código seleccionado |
| Refactorizar | Refactoriza el código |
| Generar Tests | Crea tests unitarios |
| Depurar | Encuentra y corrige errores |
| Optimizar | Mejora el rendimiento |
| Explicar | Explica el código |
| Ejecutar | Ejecuta el código |
| Chat | Abre diálogo de chat |

## Solución de Problemas

### "API desconectada"

Asegúrate de que:
1. Ollama está ejecutándose: `ollama serve`
2. La API está activa: `python api_server.py`
3. La URL es correcta en configuración

### "Modelo no disponible"

Descarga el modelo:
```bash
ollama pull llama3
```

## Arquitectura

```
IntelliJ IDEA Plugin
        │
        ▼
Kotlin HTTP Client
        │
        ▼
IA Local Vargas API (FastAPI)
        │
        ├── Code Analyzer
        ├── Language Executor
        ├── Project Creator
        └── Ollama LLM
```

## Construcción (Windows)

```bash
# Ir al directorio del plugin
cd intellij_plugin

# Instalar dependencias y construir
gradlew buildPlugin

# Si no tienes Gradle instalado, descarga gradle-wrapper
```

O alternativamente, usa el wrapper de Gradle que se descarga automáticamente con el plugin de IntelliJ en el IDE.

## Notas para Windows

- Asegúrate de tener JDK 17+ instalado
- El plugin se puede desarrollar dentro de IntelliJ IDEA importando el proyecto como proyecto de Gradle

## Estructura del Proyecto

```
intellij_plugin/
├── build.gradle.kts          # Configuración de Gradle
├── src/
│   └── main/
│       ├── kotlin/
│       │   └── com/iavargas/
│       │       ├── IaLocalVargasPlugin.kt   # Plugin principal
│       │       ├── api/
│       │       │   └── IaLocalVargasApi.kt  # Cliente HTTP
│       │       ├── actions/
│       │       │   ├── AnalyzeAction.kt    # Analizar
│       │       │   ├── RefactorAction.kt   # Refactorizar
│       │       │   ├── TestAction.kt       # Tests
│       │       │   ├── DebugAction.kt      # Depurar
│       │       │   ├── OptimizeAction.kt  # Optimizar
│       │       │   ├── ExplainAction.kt   # Explicar
│       │       │   ├── ExecuteAction.kt   # Ejecutar
│       │       │   └── ChatAction.kt       # Chat
│       │       └── config/
│       │           └── PluginSettings.kt  # Configuración
│       └── resources/
│           └── META-INF/
│               └── plugin.xml              # Manifesto
└── README.md
```

## Licencia

MIT

