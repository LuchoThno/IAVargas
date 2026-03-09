# Plan de Integración: ai_dev_system con IAVargas (VSCode + IntelliJ)

## Objetivo
Conectar el sistema ai_dev_system (agentes de IA) con IAVargas como extensiones de VSCode e IntelliJ.

## Pasos a seguir:

### 1. Extender api_server.py con endpoints de ai_dev_system
- [ ] 1.1 Añadir endpoint `/orchestrate` - Ejecutar tareas complejas
- [ ] 1.2 Añadir endpoint `/create-project` - Crear proyectos completos
- [ ] 1.3 Añadir endpoint `/agent/{agent_name}` - Acceder a agentes específicos

### 2. Actualizar Extensión VSCode
- [ ] 2.1 Añadir métodos `orchestrate()` y `createProject()` en api.ts
- [ ] 2.2 Registrar comandos en commands.ts
- [ ] 2.3 Actualizar package.json con nuevos comandos

### 3. Actualizar Plugin IntelliJ
- [ ] 3.1 Añadir métodos `orchestrate()` y `createProject()` en IaLocalVargasApi.kt
- [ ] 3.2 Crear nuevas acciones (CreateProjectAction, OrchestrateAction)
- [ ] 3.3 Actualizar plugin.xml

### 4. Integrar ai_dev_system con la API
- [ ] 4.1 Modificar orchestrator para aceptar parámetros externos
- [ ] 4.2 Añadir logging adecuado para debugging
- [ ] 4.3 Manejo de errores para IDE integration

### 5. Testing
- [ ] 5.1 Probar endpoints de API
- [ ] 5.2 Probar extensión VSCode
- [ ] 5.3 Probar plugin IntelliJ

