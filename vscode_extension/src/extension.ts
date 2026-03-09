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

import * as vscode from 'vscode';
import { ApiClient } from './api';
import { registerCommands } from './commands';
import { ExtensionConfig } from './config';
import { IaLocalVargasPanel } from './panel';
import { IaLocalVargasStatusBar } from './statusBar';

// Configuración global
let statusBar: IaLocalVargasStatusBar;
let apiClient: ApiClient;
let config: ExtensionConfig;

/**
 * Función de activación de la extensión
 * Se ejecuta cuando VSCode carga la extensión
 */
export async function activate(context: vscode.ExtensionContext): Promise<void> {
    console.log('🤖 IA Local Vargas: Activando extensión...');
    
    try {
        // Inicializar configuración
        config = new ExtensionConfig();
        
        // Inicializar cliente API
        apiClient = new ApiClient(config.apiUrl, config.model);
        
        // Verificar conexión con la API
        const health = await apiClient.checkHealth();
        if (!health.connected) {
            vscode.window.showWarningMessage(
                '⚠️ IA Local Vargas: No se pudo conectar con la API. ' +
                'Asegúrate de que api_server.py esté ejecutándose en ' + config.apiUrl
            );
        } else {
            console.log('✅ API conectada:', health);
        }
        
        // Crear barra de estado
        statusBar = new IaLocalVargasStatusBar(apiClient);
        statusBar.show();
        
        // Registrar comandos
        registerCommands(context, apiClient, config);
        
        // Crear panel lateral si está configurado
        if (vscode.workspace.getConfiguration('iaLocalVargas').get('showPanelOnStart', false)) {
            IaLocalVargasPanel.createOrShow(context.extensionUri, apiClient);
        }
        
        // Registrar proveedor de autocompletado
        registerInlineCompletionProvider(context, apiClient);
        
        // Mostrar mensaje de éxito
        const modelInfo = health.available_models?.length > 0 
            ? health.available_models[0] 
            : config.model;
            
        vscode.window.showInformationMessage(
            `✅ IA Local Vargas activada con modelo: ${modelInfo}`
        );
        
        console.log('✅ IA Local Vargas: Extensión activada correctamente');
        
    } catch (error) {
        console.error('❌ Error al activar la extensión:', error);
        vscode.window.showErrorMessage(
            '❌ Error al activar IA Local Vargas: ' + (error as Error).message
        );
    }
}

/**
 * Función de desactivación
 * Se ejecuta cuando VSCode descarga la extensión
 */
export function deactivate(): void {
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
function registerInlineCompletionProvider(
    context: vscode.ExtensionContext,
    apiClient: ApiClient
): void {
    if (!config.enableInlineCompletion) {
        return;
    }
    
    const provider = vscode.languages.registerInlineCompletionItemProvider(
        { pattern: '**/*' },
        {
            async provideInlineCompletionItems(
                document: vscode.TextDocument,
                position: vscode.Position,
                _context: vscode.InlineCompletionContext,
                token: vscode.CancellationToken
            ): Promise<vscode.InlineCompletionItem[] | undefined> {
                try {
                    // Obtener el texto antes del cursor
                    const range = new vscode.Range(
                        new vscode.Position(position.line, 0),
                        position
                    );
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
                    const items: vscode.InlineCompletionItem[] = [];
                    
                    // Dividir en líneas y tomar solo la siguiente línea sugerida
                    const lines = response.completion.split('\n');
                    if (lines.length > 0 && lines[0].trim()) {
                        items.push(new vscode.InlineCompletionItem(
                            lines[0],
                            new vscode.Range(position, position)
                        ));
                    }
                    
                    return items;
                    
                } catch (error) {
                    console.error('Error en autocompletado:', error);
                    return undefined;
                }
            }
        }
    );
    
    context.subscriptions.push(provider);
}

