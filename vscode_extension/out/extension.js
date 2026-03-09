"use strict";
/**
 * IA Local Vargas - VSCode Extension
 * ================================
 * Extensión para VSCode que integra el asistente de IA local
 *
 * Funcionalidades:
 * - Análisis de código
 * - Refactorización
 * - Generación de tests
 * - Depuración
 * - Optimización
 * - Generación de código
 * - Chat con IA
 * - Autocompletado inline
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const api_1 = require("./api");
const commands_1 = require("./commands");
const config_1 = require("./config");
const panel_1 = require("./panel");
const statusBar_1 = require("./statusBar");
// Configuración global
let statusBar;
let apiClient;
let config;
/**
 * Función de activación de la extensión
 * Se ejecuta cuando VSCode carga la extensión
 */
async function activate(context) {
    console.log('🤖 IA Local Vargas: Activando extensión...');
    try {
        // Inicializar configuración
        config = new config_1.ExtensionConfig();
        // Inicializar cliente API
        apiClient = new api_1.ApiClient(config.apiUrl, config.model);
        // Verificar conexión con la API
        const health = await apiClient.checkHealth();
        if (!health.connected) {
            vscode.window.showWarningMessage('⚠️ IA Local Vargas: No se pudo conectar con la API. ' +
                'Asegúrate de que api_server.py esté ejecutándose en ' + config.apiUrl);
        }
        else {
            console.log('✅ API conectada:', health);
        }
        // Crear barra de estado
        statusBar = new statusBar_1.IaLocalVargasStatusBar(apiClient);
        statusBar.show();
        // Registrar comandos
        (0, commands_1.registerCommands)(context, apiClient, config);
        // Crear panel lateral si está configurado
        if (vscode.workspace.getConfiguration('iaLocalVargas').get('showPanelOnStart', false)) {
            panel_1.IaLocalVargasPanel.createOrShow(context.extensionUri, apiClient);
        }
        // Registrar proveedor de autocompletado
        registerInlineCompletionProvider(context, apiClient);
        // Mostrar mensaje de éxito
        const modelInfo = health.available_models?.length > 0
            ? health.available_models[0]
            : config.model;
        vscode.window.showInformationMessage(`✅ IA Local Vargas activada con modelo: ${modelInfo}`);
        console.log('✅ IA Local Vargas: Extensión activada correctamente');
    }
    catch (error) {
        console.error('❌ Error al activar la extensión:', error);
        vscode.window.showErrorMessage('❌ Error al activar IA Local Vargas: ' + error.message);
    }
}
/**
 * Función de desactivación
 * Se ejecuta cuando VSCode descarga la extensión
 */
function deactivate() {
    console.log('👋 IA Local Vargas: Desactivando extensión...');
    if (statusBar) {
        statusBar.dispose();
    }
    if (apiClient) {
        apiClient.dispose();
    }
}
/**
 * Registra el proveedor de autocompletado inline
 */
function registerInlineCompletionProvider(context, apiClient) {
    if (!config.enableInlineCompletion) {
        return;
    }
    const provider = vscode.languages.registerInlineCompletionItemProvider({ pattern: '**/*' }, {
        async provideInlineCompletionItems(document, position, _context, token) {
            try {
                // Obtener el texto antes del cursor
                const range = new vscode.Range(new vscode.Position(position.line, 0), position);
                const textBeforeCursor = document.getText(range);
                // Solo sugerir si hay suficiente contexto
                if (textBeforeCursor.length < 10) {
                    return undefined;
                }
                // Obtener el lenguaje
                const language = document.languageId;
                // Llamar a la API para autocompletado
                const response = await apiClient.complete({
                    prefix: textBeforeCursor,
                    language: language,
                    max_tokens: 100
                }, token);
                if (!response || !response.completion) {
                    return undefined;
                }
                // Crear items de autocompletado
                const items = [];
                // Dividir en líneas y tomar solo la siguiente línea sugerida
                const lines = response.completion.split('\n');
                if (lines.length > 0 && lines[0].trim()) {
                    items.push(new vscode.InlineCompletionItem(lines[0], new vscode.Range(position, position)));
                }
                return items;
            }
            catch (error) {
                console.error('Error en autocompletado:', error);
                return undefined;
            }
        }
    });
    context.subscriptions.push(provider);
}
//# sourceMappingURL=extension.js.map