/**
 * Extension Configuration - Configuración de la Extensión
 * ======================================================
 * Maneja la configuración de VSCode para la extensión
 */

import * as vscode from 'vscode';

/**
 * Clase de configuración de la extensión
 */
export class ExtensionConfig {
    // URL de la API
    apiUrl: string;
    
    // Modelo de Ollama
    model: string;
    
    // Parámetros de generación
    temperature: number;
    maxTokens: number;
    
    // Comportamiento
    autoExecute: boolean;
    showNotifications: boolean;
    enableInlineCompletion: boolean;

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
    reload(): void {
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
    static getCurrentLanguage(): string {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return 'python'; // Default
        }
        
        const languageId = editor.document.languageId;
        
        // Mapeo de lenguajes de VSCode a lenguajes de la API
        const languageMap: Record<string, string> = {
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
    static getSelectedCode(): string | null {
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
    static getCurrentFileContent(): string | null {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return null;
        }
        
        return editor.document.getText();
    }
}

/**
 * Proveedor de configuración que escucha cambios
 */
export function registerConfigurationWatcher(
    callback: (config: ExtensionConfig) => void
): vscode.Disposable {
    return vscode.workspace.onDidChangeConfiguration((event) => {
        if (event.affectsConfiguration('iaLocalVargas')) {
            callback(new ExtensionConfig());
        }
    });
}

