/**
 * Panel - Panel WebView de IA Local Vargas
 * =========================================
 * Panel lateral con interfaz de chat
 */

import * as vscode from 'vscode';
import { ApiClient } from './api';

// ============================================
// VARIABLES GLOBALES
// ============================================

let currentPanel: vscode.WebviewPanel | undefined;
let apiClient: ApiClient;

/**
 * Mensaje del chat
 */
interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

// Historial de mensajes
let chatHistory: ChatMessage[] = [];

// ============================================
// PANEL PRINCIPAL
// ============================================

export class IaLocalVargasPanel {
    
    /**
     * Crea o muestra el panel
     */
    public static createOrShow(extensionUri: vscode.Uri, client: ApiClient): void {
        apiClient = client;

        // Si ya existe, mostrar
        if (currentPanel) {
            currentPanel.reveal(vscode.ViewColumn.One);
            return;
        }

        // Crear nuevo panel
        currentPanel = vscode.window.createWebviewPanel(
            'iaLocalVargas',
            'IA Local Vargas',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media')
                ]
            }
        );

        // Configurar contenido
        currentPanel.webview.html = this.getHtml();
        
        // Manejar mensajes desde el webview
        currentPanel.webview.onDidReceiveMessage(async (message) => {
            await this.handleMessage(message);
        });

        // Limpiar al cerrar
        currentPanel.onDidDispose(() => {
            currentPanel = undefined;
        });
    }

    /**
     * Agrega un mensaje al chat
     */
    public static addMessage(role: 'user' | 'assistant', content: string): void {
        chatHistory.push({ role, content });
        
        if (currentPanel) {
            currentPanel.webview.postMessage({
                type: 'addMessage',
                role,
                content
            });
        }
    }

    /**
     * Maneja mensajes desde el webview
     */
    private static async handleMessage(message: any): Promise<void> {
        switch (message.type) {
            case 'ask':
                await this.handleAsk(message.prompt);
                break;
            case 'clear':
                chatHistory = [];
                break;
            case 'analyze':
                await this.handleAnalyze(message.code, message.language);
                break;
            case 'execute':
                await this.handleExecute(message.code, message.language);
                break;
            case 'getSelectedCode':
                // Get selected code from the active editor
                const editor = vscode.window.activeTextEditor;
                const selectedCode = editor && !editor.selection.isEmpty
                    ? editor.document.getText(editor.selection)
                    : '';
                const currentLanguage = editor
                    ? editor.document.languageId
                    : 'python';
                this.sendMessage({ 
                    type: 'selectedCode', 
                    code: selectedCode,
                    language: currentLanguage
                });
                break;
        }
    }

    /**
     * Maneja pregunta al chat
     */
    private static async handleAsk(prompt: string): Promise<void> {
        try {
            // Agregar mensaje del usuario
            chatHistory.push({ role: 'user', content: prompt });
            this.sendMessage({ type: 'addMessage', role: 'user', content: prompt });
            
            // Indicador de carga
            this.sendMessage({ type: 'loading', loading: true });

            // Llamar API
            const response = await apiClient.ask({
                prompt,
                temperature: 0.7,
                max_tokens: 2048
            });

            // Agregar respuesta
            chatHistory.push({ role: 'assistant', content: response });
            this.sendMessage({ type: 'addMessage', role: 'assistant', content: response });
            this.sendMessage({ type: 'loading', loading: false });

        } catch (error) {
            this.sendMessage({ 
                type: 'error', 
                message: (error as Error).message 
            });
            this.sendMessage({ type: 'loading', loading: false });
        }
    }

    /**
     * Maneja análisis de código
     */
    private static async handleAnalyze(code: string, language: string): Promise<void> {
        try {
            this.sendMessage({ type: 'loading', loading: true });

            const result = await apiClient.analyze({
                code,
                language: language || 'python',
                include_security: true,
                include_complexity: true
            });

            const response = `
📊 **Análisis de Código**

Líneas: ${result.lines}
Puntuación: ${result.score}/100

${result.security_issues.length > 0 ? `⚠️ **Problemas de Seguridad:**\n${result.security_issues.map(i => `- ${i.message}`).join('\n')}` : '✅ Sin problemas de seguridad'}

📈 **Complejidad:** ${result.complexity.cyclomatic}

💡 **Sugerencias:**
${result.suggestions.slice(0, 3).map(s => `- ${s}`).join('\n')}
            `;

            chatHistory.push({ role: 'assistant', content: response });
            this.sendMessage({ type: 'addMessage', role: 'assistant', content: response });
            this.sendMessage({ type: 'loading', loading: false });

        } catch (error) {
            this.sendMessage({ 
                type: 'error', 
                message: (error as Error).message 
            });
            this.sendMessage({ type: 'loading', loading: false });
        }
    }

    /**
     * Maneja ejecución de código
     */
    private static async handleExecute(code: string, language: string): Promise<void> {
        try {
            this.sendMessage({ type: 'loading', loading: true });

            const result = await apiClient.execute({
                code,
                language,
                timeout: 30
            });

            const response = `
🚀 **Ejecución ${language}**

${result.success ? '✅ Éxito' : '❌ Error'}

${result.stdout ? `📤 **Salida:**\n${result.stdout}` : ''}
${result.stderr ? `⚠️ **Error:**\n${result.stderr}` : ''}
            `;

            chatHistory.push({ role: 'assistant', content: response });
            this.sendMessage({ type: 'addMessage', role: 'assistant', content: response });
            this.sendMessage({ type: 'loading', loading: false });

        } catch (error) {
            this.sendMessage({ 
                type: 'error', 
                message: (error as Error).message 
            });
            this.sendMessage({ type: 'loading', loading: false });
        }
    }

    /**
     * Envía mensaje al webview
     */
    private static sendMessage(message: any): void {
        if (currentPanel) {
            currentPanel.webview.postMessage(message);
        }
    }

    /**
     * Obtiene el HTML del panel
     */
    private static getHtml(): string {
        return `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA Local Vargas</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: #252526;
            padding: 16px;
            border-bottom: 1px solid #3c3c3c;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .header h1 {
            font-size: 18px;
            font-weight: 600;
            color: #569cd6;
        }
        
        .header .status {
            margin-left: auto;
            font-size: 12px;
            color: #6a9955;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }
        
        .message {
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 8px;
            max-width: 90%;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: #264f78;
            margin-left: auto;
        }
        
        .message.assistant {
            background: #2d2d2d;
        }
        
        .message .role {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 4px;
            opacity: 0.7;
        }
        
        .message.user .role { color: #9cdcfe; }
        .message.assistant .role { color: #ce9178; }
        
        .message .content {
            white-space: pre-wrap;
            line-height: 1.5;
        }
        
        .message .content code {
            background: #1a1a1a;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
        }
        
        .input-container {
            padding: 16px;
            background: #252526;
            border-top: 1px solid #3c3c3c;
        }
        
        .input-wrapper {
            display: flex;
            gap: 8px;
        }
        
        #messageInput {
            flex: 1;
            background: #3c3c3c;
            border: 1px solid #3c3c3c;
            color: #d4d4d4;
            padding: 12px;
            border-radius: 6px;
            resize: none;
            font-family: inherit;
            font-size: 14px;
        }
        
        #messageInput:focus {
            outline: none;
            border-color: #569cd6;
        }
        
        button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }
        
        button:hover {
            background: #1177bb;
        }
        
        button:disabled {
            background: #3c3c3c;
            cursor: not-allowed;
        }
        
        .actions {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            flex-wrap: wrap;
        }
        
        .action-btn {
            background: #3c3c3c;
            padding: 6px 12px;
            font-size: 12px;
        }
        
        .action-btn:hover {
            background: #505050;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #6a9955;
        }
        
        .error {
            background: #4b1818;
            color: #f48771;
            padding: 12px;
            border-radius: 6px;
            margin: 8px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 IA Local Vargas</h1>
        <span class="status">● Conectado</span>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message assistant">
            <div class="role">Asistente</div>
            <div class="content">¡Hola! Soy tu asistente de IA local. ¿En qué puedo ayudarte hoy?</div>
        </div>
    </div>
    
    <div class="input-container">
        <div class="input-wrapper">
            <textarea id="messageInput" placeholder="Escribe tu mensaje..." rows="2"></textarea>
            <button id="sendBtn">Enviar</button>
        </div>
        <div class="actions">
            <button class="action-btn" onclick="analyzeCode()">📊 Analizar</button>
            <button class="action-btn" onclick="executeCode()">▶️ Ejecutar</button>
            <button class="action-btn" onclick="clearChat()">🗑️ Limpiar</button>
        </div>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // Enviar mensaje
        function sendMessage() {
            const content = messageInput.value.trim();
            if (!content) return;
            
            vscode.postMessage({ type: 'ask', prompt: content });
            messageInput.value = '';
        }
        
        sendBtn.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Track which action requested the selected code
        let pendingAction = null;
        
        // Analizar código seleccionado
        function analyzeCode() {
            pendingAction = 'analyze';
            vscode.postMessage({ type: 'getSelectedCode' });
        }
        
        // Ejecutar código
        function executeCode() {
            pendingAction = 'execute';
            vscode.postMessage({ type: 'getSelectedCode' });
        }
        
        // Limpiar chat
        function clearChat() {
            chatContainer.innerHTML = '';
            vscode.postMessage({ type: 'clear' });
        }
        
        // Recibir mensajes
        window.addEventListener('message', (event) => {
            const message = event.data;
            
            if (message.type === 'selectedCode') {
                if (message.code && pendingAction) {
                    // Send analyze/execute with actual code and language
                    if (pendingAction === 'analyze') {
                        vscode.postMessage({ 
                            type: 'analyze', 
                            code: message.code,
                            language: message.language
                        });
                    } else if (pendingAction === 'execute') {
                        vscode.postMessage({ 
                            type: 'execute', 
                            code: message.code,
                            language: message.language
                        });
                    }
                    pendingAction = null;
                } else {
                    // No code selected - show message
                    addError('Selecciona código en el editor primero');
                    pendingAction = null;
                }
            } else if (message.type === 'addMessage') {
                addMessage(message.role, message.content);
            } else if (message.type === 'loading') {
                sendBtn.disabled = message.loading;
                sendBtn.textContent = message.loading ? '...' : 'Enviar';
            } else if (message.type === 'error') {
                addError(message.message);
            }
        });
        
        function addMessage(role, content) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.innerHTML = '<div class="role">' + role + '</div><div class="content">' + content + '</div>';
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function addError(message) {
            const div = document.createElement('div');
            div.className = 'error';
            div.textContent = 'Error: ' + message;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>`;
    }
}

