"use strict";
/**
 * API Client - Cliente para IA Local Vargas API
 * =============================================
 * Maneja todas las comunicaciones con el servidor FastAPI
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiClient = void 0;
// ============================================
// CLIENTE API
// ============================================
class ApiClient {
    baseUrl;
    model;
    timeout;
    constructor(baseUrl, model) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remover trailing slash
        this.model = model;
        this.timeout = 60000; // 60 segundos timeout para dar tiempo a Ollama
    }
    /**
     * Verifica el estado de la API
     */
    async checkHealth() {
        try {
            const response = await this.request('/health', 'GET');
            const isConnected = response.status === 'healthy';
            return {
                status: response.status || 'unhealthy',
                ollama: response.ollama === 'connected' ? 'connected' : 'disconnected',
                model: response.model || this.model,
                available_models: response.available_models || [],
                connected: isConnected
            };
        }
        catch (error) {
            return {
                status: 'unhealthy',
                ollama: 'disconnected',
                model: this.model,
                available_models: [],
                connected: false
            };
        }
    }
    /**
     * Envía una pregunta general a la IA
     */
    async ask(request) {
        const response = await this.request('/ask', 'POST', {
            prompt: request.prompt,
            temperature: request.temperature ?? 0.7,
            max_tokens: request.max_tokens ?? 2048,
            context: request.context
        });
        if (!response.success) {
            throw new Error(response.error || 'Error desconocido');
        }
        return response.result;
    }
    /**
     * Analiza código
     */
    async analyze(request) {
        const response = await this.request('/analyze', 'POST', {
            code: request.code,
            language: request.language,
            include_security: request.include_security ?? true,
            include_complexity: request.include_complexity ?? true
        });
        if (!response.success) {
            throw new Error(response.error || 'Error al analizar');
        }
        return response.result;
    }
    /**
     * Refactoriza código
     */
    async refactor(request) {
        const response = await this.request('/refactor', 'POST', {
            code: request.code,
            language: request.language,
            style: request.style ?? 'default',
            goal: request.goal
        });
        if (!response.success) {
            throw new Error(response.error || 'Error al refactorizar');
        }
        return response.result.refactored_code || response.result;
    }
    /**
     * Genera tests
     */
    async generateTests(request) {
        const response = await this.request('/test', 'POST', {
            code: request.code,
            language: request.language,
            framework: request.framework,
            test_count: request.test_count ?? 3
        });
        if (!response.success) {
            throw new Error(response.error || 'Error al generar tests');
        }
        return response.result.tests || response.result;
    }
    /**
     * Ejecuta código
     */
    async execute(request) {
        const response = await this.request('/execute', 'POST', {
            code: request.code,
            language: request.language,
            timeout: request.timeout ?? 30
        });
        if (!response.success) {
            return {
                success: false,
                stdout: '',
                stderr: response.error || 'Error desconocido',
                exit_code: -1,
                error: response.error
            };
        }
        return response.result;
    }
    /**
     * Genera código
     */
    async generate(request) {
        const response = await this.request('/generate', 'POST', {
            description: request.description,
            language: request.language,
            project_type: request.project_type
        });
        if (!response.success) {
            throw new Error(response.error || 'Error al generar código');
        }
        return typeof response.result === 'string'
            ? response.result
            : JSON.stringify(response.result, null, 2);
    }
    /**
     * Depura código
     */
    async debug(request) {
        const response = await this.request('/debug', 'POST', {
            code: request.code,
            language: request.language,
            error_message: request.error_message
        });
        if (!response.success) {
            throw new Error(response.error || 'Error al depurar');
        }
        return response.result.fixed_code || response.result;
    }
    /**
     * Optimiza código
     */
    async optimize(request) {
        const response = await this.request('/optimize', 'POST', {
            code: request.code,
            language: request.language,
            focus: request.focus ?? 'performance'
        });
        if (!response.success) {
            throw new Error(response.error || 'Error al optimizar');
        }
        return response.result.optimized_code || response.result;
    }
    /**
     * Autocompletado inline
     */
    async complete(request, token) {
        // Usamos el endpoint /ask para autocompletado
        const prompt = `Completa el siguiente código ${request.language}. 
Solo devuelve la continuación, sin explicaciones:

Código existente:
${request.prefix}`;
        const response = await this.request('/ask', 'POST', {
            prompt,
            temperature: 0.3, // Más preciso para autocompletado
            max_tokens: request.max_tokens ?? 100
        }, token);
        return {
            completion: response.result || ''
        };
    }
    /**
     * Orquestar una tarea compleja
     */
    async orchestrate(request) {
        const response = await this.request('/orchestrate', 'POST', {
            task: request.task,
            workspace: request.workspace ?? 'workspace/projects',
            model: request.model ?? this.model,
            max_iterations: request.max_iterations ?? 10
        });
        if (!response.success) {
            throw new Error(response.error || 'Error en orquestación');
        }
        return response.result;
    }
    /**
     * Crear un proyecto completo
     */
    async createProject(request) {
        const response = await this.request('/create-project', 'POST', {
            description: request.description,
            workspace: request.workspace ?? 'workspace/projects',
            language: request.language
        });
        if (!response.success) {
            throw new Error(response.error || 'Error creando proyecto');
        }
        return response.result;
    }
    /**
     * Ejecutar un comando de agente
     */
    async executeAgentCommand(command, code, params) {
        const response = await this.request(`/agent/${command}`, 'POST', {
            command,
            code,
            params: params ?? {}
        });
        if (!response.success) {
            throw new Error(response.error || 'Error en comando de agente');
        }
        return response.result;
    }
    /**
     * Listar agentes disponibles
     */
    async listAgents() {
        const response = await this.request('/agents', 'GET');
        if (!response.success) {
            throw new Error(response.error || 'Error listando agentes');
        }
        return response.result;
    }
    /**
     * Realiza una petición HTTP genérica
     */
    async request(endpoint, method = 'GET', body, token) {
        const url = `${this.baseUrl}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        if (token) {
            token.onCancellationRequested(() => controller.abort());
        }
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: body ? JSON.stringify(body) : undefined,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        }
        catch (error) {
            clearTimeout(timeoutId);
            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('La solicitud fue cancelada');
                }
                throw error;
            }
            throw new Error('Error desconocido al conectar con la API');
        }
    }
    /**
     * Limpia recursos
     */
    dispose() {
        // No hay recursos persistentes que liberar
    }
}
exports.ApiClient = ApiClient;
//# sourceMappingURL=api.js.map