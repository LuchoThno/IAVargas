# IA Local Vargas - VSCode Extension

Extensión de VSCode que integra el asistente de IA local con tu IDE.

## Características

- 🤖 **Chat con IA**: Pregunta a tu asistente de IA local
- 📊 **Análisis de Código**: Detecta problemas de seguridad y complejidad
- 🔄 **Refactorización**: Mejora tu código automáticamente
- 🧪 **Generación de Tests**: Crea tests unitarios
- 🐛 **Depuración**: Encuentra y corrige errores
- ⚡ **Optimización**: Mejora el rendimiento
- 💻 **Ejecución**: Ejecuta código directamente
- ✨ **Autocompletado Inline**: Sugiere código mientras escribes

## Requisitos

- [VSCode](https://code.visualstudio.com/) 1.75+
- [Ollama](https://ollama.ai/) instalado y ejecutándose
- API de IA Local Vargas ejecutándose (`python api_server.py`)

## Instalación

### Opción 1: Desde VSIX (Recomendado)

1. Descarga el archivo `.vsix` de la extensión
2. Abre VSCode
3. Ve a Extensiones (Ctrl+Shift+X)
4. Haz clic en "..." > "Instalar desde archivo VSIX"
5. Selecciona el archivo descargado

### Opción 2: Desarrollo local (Windows)

```batch
cd vscode_extension
call build.bat
```

O manualmente:
```batch
cd vscode_extension
npm install
npm run compile
npm run package
```

### Opción 3: Desarrollo local (Linux/Mac)

```bash
# Clonar el repositorio
git clone <repo-url>
cd IAVargas

# Instalar dependencias
cd vscode_extension
npm install

# Compilar
npm run compile

# Paquetizar
npm run package

# Instalar el .vsix generado
code --install-extension ia-local-vargas-1.0.0.vsix
```

## Configuración

Ve a `Configuración > Extensiones > IA Local Vargas`:

| Opción | Descripción | Default |
|--------|-------------|---------|
| `apiUrl` | URL de la API | `http://localhost:8000` |
| `model` | Modelo de Ollama | `llama3` |
| `temperature` | Creatividad (0-1) | `0.7` |
| `maxTokens` | Máx. tokens | `2048` |
| `autoExecute` | Auto-ejecutar código | `false` |
| `showNotifications` | Mostrar notificaciones | `true` |
| `enableInlineCompletion` | Autocompletado inline | `true` |

## Comandos

Accesibles desde:
- Paleta de comandos (Ctrl+Shift+P)
- Menú contextual del editor
- Atajos de teclado

| Comando | Atajo | Descripción |
|---------|-------|-------------|
| `IA: Preguntar` | Ctrl+Shift+I | Enviar pregunta |
| `IA: Analizar` | Ctrl+Shift+A | Analizar código |
| `IA: Refactorizar` | Ctrl+Shift+R | Refactorizar |
| `IA: Generar tests` | - | Crear tests |
| `IA: Depurar` | - | Corregir errores |
| `IA: Optimizar` | - | Mejorar rendimiento |
| `IA: Generar código` | - | Crear código nuevo |
| `IA: Explicar` | - | Explicar código |
| `IA: Ejecutar` | - | Ejecutar código |
| `IA: Mostrar panel` | - | Abrir panel de chat |
| `IA: Estado` | - | Ver estado del sistema |

## Uso

### Análisis de Código

1. Selecciona el código en el editor
2. Haz clic derecho > "IA: Analizar"
3. Ve los resultados en el canal de salida

### Chat

1. Presiona Ctrl+Shift+P
2. Escribe "IA: Mostrar panel"
3. Escribe tu pregunta en el panel

### Autocompletado

Escribe código y la IA sugerirá completaciones inline.

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

### Errores de compilación

```bash
# Limpiar y recompilar
rm -rf out node_modules
npm install
npm run compile
```

## Arquitectura

```
VSCode Extension
      │
      ▼
API Client (src/api.ts)
      │
      ▼
IA Local Vargas API (FastAPI)
      │
      ├── Code Analyzer
      ├── Language Executor
      ├── Project Creator
      └── Ollama LLM
```

## Licencia

MIT

