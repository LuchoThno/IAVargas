"use strict";
/**
 * Extension Configuration - Configuración de la Extensión
 * ======================================================
 * Maneja la configuración de VSCode para la extensión
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
exports.ExtensionConfig = void 0;
exports.registerConfigurationWatcher = registerConfigurationWatcher;
const vscode = __importStar(require("vscode"));
/**
 * Clase de configuración de la extensión
 */
class ExtensionConfig {
    // URL de la API
    apiUrl;
    // Modelo de Ollama
    model;
    // Parámetros de generación
    temperature;
    maxTokens;
    // Comportamiento
    autoExecute;
    showNotifications;
    enableInlineCompletion;
    constructor() {
        const config = vscode.workspace.getConfiguration('iaLocalVargas');
        this.apiUrl = config.get('apiUrl', 'http://localhost:8000');
        this.model = config.get('model', 'llama3');
        this.temperature = config.get('temperature', 0.7);
        this.maxTokens = config.get('maxTokens', 2048);
        this.autoExecute = config.get('autoExecute', false);
        this.showNotifications = config.get('showNotifications', true);
        this.enableInlineCompletion = config.get('enableInlineCompletion', true);
    }
    /**
     * Recarga la configuración desde VSCode
     */
    reload() {
        const config = vscode.workspace.getConfiguration('iaLocalVargas');
        this.apiUrl = config.get('apiUrl', 'http://localhost:8000');
        this.model = config.get('model', 'llama3');
        this.temperature = config.get('temperature', 0.7);
        this.maxTokens = config.get('maxTokens', 2048);
        this.autoExecute = config.get('autoExecute', false);
        this.showNotifications = config.get('showNotifications', true);
        this.enableInlineCompletion = config.get('enableInlineCompletion', true);
    }
    /**
     * Obtiene el lenguaje actual del editor
     */
    static getCurrentLanguage() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return 'python'; // Default
        }
        const languageId = editor.document.languageId;
        // Mapeo de lenguajes de VSCode a lenguajes de la API
        const languageMap = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'typescript',
            'java': 'java',
            'csharp': 'csharp',
            'cpp': 'cpp',
            'c': 'c',
            'go': 'go',
            'rust': 'rust',
            'ruby': 'ruby',
            'php': 'php',
            'swift': 'swift',
            'kotlin': 'kotlin',
            'scala': 'scala',
            'html': 'html',
            'css': 'css',
            'scss': 'scss',
            'json': 'json',
            'yaml': 'yaml',
            'xml': 'xml',
            'sql': 'sql',
            'shell': 'bash',
            'bash': 'bash',
            'powershell': 'powershell'
        };
        return languageMap[languageId] || 'python';
    }
    /**
     * Obtiene el código seleccionado actualmente
     */
    static getSelectedCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No hay un editor activo. Abre un archivo primero.');
            return null;
        }
        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showWarningMessage('Selecciona código en el editor primero.');
            return null;
        }
        return editor.document.getText(selection);
    }
    /**
     * Obtiene todo el contenido del archivo actual
     */
    static getCurrentFileContent() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return null;
        }
        return editor.document.getText();
    }
}
exports.ExtensionConfig = ExtensionConfig;
/**
 * Proveedor de configuración que escucha cambios
 */
function registerConfigurationWatcher(callback) {
    return vscode.workspace.onDidChangeConfiguration((event) => {
        if (event.affectsConfiguration('iaLocalVargas')) {
            callback(new ExtensionConfig());
        }
    });
}
//# sourceMappingURL=config.js.map