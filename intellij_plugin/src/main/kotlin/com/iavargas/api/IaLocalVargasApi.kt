package com.iavargas.api

import com.google.gson.Gson
import com.google.gson.JsonObject
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * Cliente API para IA Local Vargas
 */
class IaLocalVargasApi(
    private val baseUrl: String,
    private val model: String = "llama3"
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()
    
    /**
     * Estado de salud de la API
     */
    data class HealthStatus(
        val isConnected: Boolean,
        val status: String,
        val model: String,
        val availableModels: List<String>
    )
    
    /**
     * Resultado de análisis
     */
    data class AnalysisResult(
        val language: String,
        val lines: Int,
        val score: Int,
        val securityIssues: List<SecurityIssue>,
        val complexity: ComplexityMetrics,
        val suggestions: List<String>
    )
    
    data class SecurityIssue(
        val type: String,
        val severity: String,
        val message: String
    )
    
    data class ComplexityMetrics(
        val cyclomatic: Int,
        val functions: Int,
        val classes: Int,
        val imports: Int,
        val lines: Int
    )
    
    /**
     * Resultado de ejecución
     */
    data class ExecutionResult(
        val success: Boolean,
        val stdout: String,
        val stderr: String,
        val exitCode: Int
    )
    
    /**
     * Verifica el estado de la API
     */
    fun health(): HealthStatus {
        return try {
            val request = Request.Builder()
                .url("$baseUrl/health")
                .get()
                .build()
            
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val body = response.body?.string()
                val json = gson.fromJson(body, JsonObject::class.java)
                
                HealthStatus(
                    isConnected = true,
                    status = json.get("status")?.asString ?: "unknown",
                    model = json.get("model")?.asString ?: model,
                    availableModels = json.getAsJsonArray("available_models")
                        ?.map { it.asString } ?: emptyList()
                )
            } else {
                HealthStatus(false, "error", model, emptyList())
            }
        } catch (e: Exception) {
            HealthStatus(false, "error: ${e.message}", model, emptyList())
        }
    }
    
    /**
     * Envía una pregunta a la IA
     */
    fun ask(prompt: String, temperature: Double = 0.7, maxTokens: Int = 2048): String {
        val body = mapOf(
            "prompt" to prompt,
            "temperature" to temperature,
            "max_tokens" to maxTokens
        )
        
        val request = Request.Builder()
            .url("$baseUrl/ask")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            json.get("result")?.asString ?: ""
        }
    }
    
    /**
     * Analiza código
     */
    fun analyze(code: String, language: String = "python"): AnalysisResult {
        val body = mapOf(
            "code" to code,
            "language" to language,
            "include_security" to true,
            "include_complexity" to true
        )
        
        val request = Request.Builder()
            .url("$baseUrl/analyze")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            
            AnalysisResult(
                language = result.get("language")?.asString ?: language,
                lines = result.get("lines")?.asInt ?: 0,
                score = result.get("score")?.asInt ?: 0,
                securityIssues = result.getAsJsonArray("security_issues")
                    ?.map { it.asJsonObject.let { obj ->
                        SecurityIssue(
                            type = obj.get("type")?.asString ?: "",
                            severity = obj.get("severity")?.asString ?: "",
                            message = obj.get("message")?.asString ?: ""
                        )
                    }} ?: emptyList(),
                complexity = result.getAsJsonObject("complexity")?.let { obj ->
                    ComplexityMetrics(
                        cyclomatic = obj.get("cyclomatic")?.asInt ?: 0,
                        functions = obj.get("functions")?.asInt ?: 0,
                        classes = obj.get("classes")?.asInt ?: 0,
                        imports = obj.get("imports")?.asInt ?: 0,
                        lines = obj.get("lines")?.asInt ?: 0
                    )
                } ?: ComplexityMetrics(0, 0, 0, 0, 0),
                suggestions = result.getAsJsonArray("suggestions")
                    ?.map { it.asString } ?: emptyList()
            )
        }
    }
    
    /**
     * Refactoriza código
     */
    fun refactor(code: String, language: String = "python", style: String = "default"): String {
        val body = mapOf(
            "code" to code,
            "language" to language,
            "style" to style
        )
        
        val request = Request.Builder()
            .url("$baseUrl/refactor")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            result.get("refactored_code")?.asString ?: ""
        }
    }
    
    /**
     * Genera tests
     */
    fun generateTests(code: String, language: String = "python", framework: String = "pytest"): String {
        val body = mapOf(
            "code" to code,
            "language" to language,
            "framework" to framework,
            "test_count" to 3
        )
        
        val request = Request.Builder()
            .url("$baseUrl/test")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            result.get("tests")?.asString ?: ""
        }
    }
    
    /**
     * Depura código
     */
    fun debug(code: String, language: String = "python"): String {
        val body = mapOf(
            "code" to code,
            "language" to language
        )
        
        val request = Request.Builder()
            .url("$baseUrl/debug")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            result.get("fixed_code")?.asString ?: ""
        }
    }
    
    /**
     * Optimiza código
     */
    fun optimize(code: String, language: String = "python"): String {
        val body = mapOf(
            "code" to code,
            "language" to language,
            "focus" to "performance"
        )
        
        val request = Request.Builder()
            .url("$baseUrl/optimize")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            result.get("optimized_code")?.asString ?: ""
        }
    }
    
    /**
     * Ejecuta código
     */
    fun execute(code: String, language: String = "python", timeout: Int = 30): ExecutionResult {
        val body = mapOf(
            "code" to code,
            "language" to language,
            "timeout" to timeout
        )
        
        val request = Request.Builder()
            .url("$baseUrl/execute")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            
            ExecutionResult(
                success = result.get("success")?.asBoolean ?: false,
                stdout = result.get("stdout")?.asString ?: "",
                stderr = result.get("stderr")?.asString ?: "",
                exitCode = result.get("exit_code")?.asInt ?: -1
            )
        }
    }
    
    /**
     * Genera código
     */
    fun generate(description: String, language: String = "python"): String {
        val body = mapOf(
            "description" to description,
            "language" to language
        )
        
        val request = Request.Builder()
            .url("$baseUrl/generate")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.get("result")
            if (result.isJsonObject) {
                gson.toJson(result)
            } else {
                result.asString
            }
        }
    }
    
    /**
     * Resultado de orquestación
     */
    data class OrchestrationResult(
        val status: String,
        val iterations: Int,
        val output: String,
        val error: String,
        val plan: String,
        val history: List<String>
    )
    
    /**
     * Lista de agentes
     */
    data class AgentsList(
        val agents: List<String>,
        val count: Int
    )
    
    /**
     * Orquestar una tarea compleja
     */
    fun orchestrate(task: String, workspace: String = "workspace/projects", maxIterations: Int = 10): OrchestrationResult {
        val body = mapOf(
            "task" to task,
            "workspace" to workspace,
            "max_iterations" to maxIterations
        )
        
        val request = Request.Builder()
            .url("$baseUrl/orchestrate")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            
            OrchestrationResult(
                status = result.get("status")?.asString ?: "unknown",
                iterations = result.get("iterations")?.asInt ?: 0,
                output = result.get("output")?.asString ?: "",
                error = result.get("error")?.asString ?: "",
                plan = gson.toJson(result.get("plan")),
                history = result.getAsJsonArray("history")
                    ?.map { it.asString } ?: emptyList()
            )
        }
    }
    
    /**
     * Crear un proyecto completo
     */
    fun createProject(description: String, language: String = "python", workspace: String = "workspace/projects"): OrchestrationResult {
        val body = mapOf(
            "description" to description,
            "language" to language,
            "workspace" to workspace
        )
        
        val request = Request.Builder()
            .url("$baseUrl/create-project")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            
            OrchestrationResult(
                status = result.get("status")?.asString ?: "unknown",
                iterations = result.get("iterations")?.asInt ?: 0,
                output = result.get("output")?.asString ?: "",
                error = result.get("error")?.asString ?: "",
                plan = gson.toJson(result.get("plan")),
                history = result.getAsJsonArray("history")
                    ?.map { it.asString } ?: emptyList()
            )
        }
    }
    
    /**
     * Ejecutar un comando de agente
     */
    fun executeAgentCommand(command: String, code: String, params: Map<String, Any> = emptyMap()): String {
        val body = mapOf(
            "command" to command,
            "code" to code,
            "params" to params
        )
        
        val request = Request.Builder()
            .url("$baseUrl/agent/$command")
            .post(gson.toJson(body).toRequestBody(jsonMediaType))
            .build()
        
        return executeRequest(request) { json ->
            json.get("result")?.asString ?: ""
        }
    }
    
    /**
     * Listar agentes disponibles
     */
    fun listAgents(): AgentsList {
        val request = Request.Builder()
            .url("$baseUrl/agents")
            .get()
            .build()
        
        return executeRequest(request) { json ->
            val result = json.getAsJsonObject("result")
            
            AgentsList(
                agents = result.getAsJsonArray("agents")
                    ?.map { it.asString } ?: emptyList(),
                count = result.get("count")?.asInt ?: 0
            )
        }
    }
    
    /**
     * Ejecuta una request y parsea el resultado
     */
    private inline fun <T> executeRequest(request: Request, parser: (JsonObject) -> T): T {
        try {
            val response = client.newCall(request).execute()
            
            if (!response.isSuccessful) {
                throw IOException("Error: ${response.code} - ${response.message}")
            }
            
            val body = response.body?.string()
            val json = gson.fromJson(body, JsonObject::class.java)
            
            if (json.get("success")?.asBoolean == true) {
                return parser(json)
            } else {
                throw IOException(json.get("error")?.asString ?: "Error desconocido")
            }
        } catch (e: Exception) {
            throw IOException("Error de conexión: ${e.message}", e)
        }
    }
}

