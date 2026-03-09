/**
 * API Client - Cliente para IA Local Vargas API
 * =============================================
 * Maneja todas las comunicaciones con el servidor FastAPI
 */

import * as vscode from 'vscode';

// ============================================
// TIPOS DE DATOS
// ============================================

export interface ApiResponse<T = any> {
    success: boolean;
    result: T;
    error?: string;
}

export interface HealthStatus {
    status: 'healthy' | 'unhealthy';
    ollama: 'connected' | 'disconnected';
    model: string;
    available_models: string[];
    connected?: boolean; // Compatibilidad con la extensión
}

export interface AskRequest {
    prompt: string;
    temperature?: number;
    max_tokens?: number;
    context?: Record<string, string>;
}

export interface AnalyzeRequest {
    code: string;
    language: string;
    include_security?: boolean;
    include_complexity?: boolean;
}

export interface RefactorRequest {
    code: string;
    language: string;
    style?: string;
    goal?: string;
}

export interface TestRequest {
    code: string;
    language: string;
    framework?: string;
    test_count?: number;
}

export interface ExecuteRequest {
    code: string;
    language: string;
    timeout?: number;
}

export interface GenerateRequest {
    description: string;
    language: string;
    project_type?: string;
}

export interface DebugRequest {
    code: string;
    language: string;
    error_message?: string;
}

export interface OptimizeRequest {
    code: string;
    language: string;
    focus?: 'performance' | 'memory' | 'readability';
}

export interface CompletionRequest {
    prefix: string;
    language: string;
    max_tokens?: number;
}

export interface AnalysisResult {
    language: string;
    lines: number;
    issues: any[];
    security_issues: SecurityIssue[];
    complexity: ComplexityMetrics;
    suggestions: string[];
    score: number;
}

export interface SecurityIssue {
    type: string;
    severity: string;
    message: string;
    pattern?: string;
}

export interface ComplexityMetrics {
    cyclomatic: number;
    functions: number;
    classes: number;
    imports: number;
    lines: number;
}

export interface ExecutionResult {
    success: boolean;
    stdout: string;
    stderr: string;
    exit_code: number;
    error?: string;
}

// ============================================
// TIPOS ai_dev_system
// ============================================

export interface OrchestrateRequest {
    task: string;
    workspace?: string;
    model?: string;
    max_iterations?: number;
}

export interface CreateProjectRequest {
    description: string;
    workspace?: string;
    language: string;
}

export interface AgentCommandRequest {
    command: string;
    code: string;
    params?: Record<string, any>;
}

export interface OrchestrationResult {
    status: string;
    iterations: number;
    output: string;
    error: string;
    plan: any;
    history: string[];
}

export interface AgentsList {
    agents: string[];
    count: number;
}

// ============================================
// CLIENTE API
// ============================================

export class ApiClient {
    private baseUrl: string;
    private model: string;
    private timeout: number;

    constructor(baseUrl: string, model: string) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remover trailing slash
        this.model = model;
        this.timeout = 60000; // 60 segundos timeout para dar tiempo a Ollama
    }

    /**
     * Verifica el estado de la API
     */
    async checkHealth(): Promise<HealthStatus> {
        try {
            const response = await this.request<any>('/health', 'GET');
            const isConnected = response.status === 'healthy';
            return {
                status: response.status || 'unhealthy',
                ollama: response.ollama === 'connected' ? 'connected' : 'disconnected',
                model: response.model || this.model,
                available_models: response.available_models || [],
                connected: isConnected
            };
        } catch (error) {
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
    async ask(request: AskRequest): Promise<string> {
        const response = await this.request<ApiResponse>('/ask', 'POST', {
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
    async analyze(request: AnalyzeRequest): Promise<AnalysisResult> {
        const response = await this.request<ApiResponse<AnalysisResult>>('/analyze', 'POST', {
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
    async refactor(request: RefactorRequest): Promise<string> {
        const response = await this.request<ApiResponse>('/refactor', 'POST', {
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
    async generateTests(request: TestRequest): Promise<string> {
        const response = await this.request<ApiResponse>('/test', 'POST', {
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
    async execute(request: ExecuteRequest): Promise<ExecutionResult> {
        const response = await this.request<ApiResponse<ExecutionResult>>('/execute', 'POST', {
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
    async generate(request: GenerateRequest): Promise<string> {
        const response = await this.request<ApiResponse>('/generate', 'POST', {
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
    async debug(request: DebugRequest): Promise<string> {
        const response = await this.request<ApiResponse>('/debug', 'POST', {
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
    async optimize(request: OptimizeRequest): Promise<string> {
        const response = await this.request<ApiResponse>('/optimize', 'POST', {
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
    async complete(request: CompletionRequest, token?: vscode.CancellationToken): Promise<{ completion: string }> {
        // Usamos el endpoint /ask para autocompletado
        const prompt = `Completa el siguiente código ${request.language}. 
Solo devuelve la continuación, sin explicaciones:

Código existente:
${request.prefix}`;

        const response = await this.request<ApiResponse>(
            '/ask', 
            'POST', 
            {
                prompt,
                temperature: 0.3, // Más preciso para autocompletado
                max_tokens: request.max_tokens ?? 100
            },
            token
        );

        return {
            completion: response.result || ''
        };
    }

    /**
     * Orquestar una tarea compleja
     */
    async orchestrate(request: OrchestrateRequest): Promise<OrchestrationResult> {
        const response = await this.request<ApiResponse<OrchestrationResult>>('/orchestrate', 'POST', {
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
    async createProject(request: CreateProjectRequest): Promise<OrchestrationResult> {
        const response = await this.request<ApiResponse<OrchestrationResult>>('/create-project', 'POST', {
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
    async executeAgentCommand(command: string, code: string, params?: Record<string, any>): Promise<string> {
        const response = await this.request<ApiResponse>(
            `/agent/${command}`, 
            'POST',
            {
                command,
                code,
                params: params ?? {}
            }
        );

        if (!response.success) {
            throw new Error(response.error || 'Error en comando de agente');
        }

        return response.result;
    }

    /**
     * Listar agentes disponibles
     */
    async listAgents(): Promise<AgentsList> {
        const response = await this.request<ApiResponse<AgentsList>>('/agents', 'GET');

        if (!response.success) {
            throw new Error(response.error || 'Error listando agentes');
        }

        return response.result;
    }

    /**
     * Realiza una petición HTTP genérica
     */
    private async request<T>(
        endpoint: string,
        method: 'GET' | 'POST' = 'GET',
        body?: any,
        token?: vscode.CancellationToken
    ): Promise<T> {
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

            return await response.json() as T;
            
        } catch (error) {
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
    dispose(): void {
        // No hay recursos persistentes que liberar
    }
}

