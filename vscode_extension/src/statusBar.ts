/**
 * StatusBar - Barra de Estado
 * ========================
 * Muestra el estado de la IA en la barra de estado de VSCode
 */

import * as vscode from 'vscode';
import { ApiClient } from './api';

/**
 * Manejador de la barra de estado
 */
export class IaLocalVargasStatusBar {
    private statusBarItem: vscode.StatusBarItem;
    private apiClient: ApiClient;
    private updateInterval: NodeJS.Timeout | null = null;

    constructor(apiClient: ApiClient) {
        this.apiClient = apiClient;
        
        // Crear elemento de barra de estado
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        
        this.statusBarItem.command = 'iaLocalVargas.showPanel';
        this.statusBarItem.tooltip = 'IA Local Vargas - Click para abrir';
        
        // Actualizar estado inicial
        this.updateStatus();
        
        // Actualizar cada 30 segundos
        this.updateInterval = setInterval(() => {
            this.updateStatus();
        }, 30000);
    }

    /**
     * Muestra la barra de estado
     */
    show(): void {
        this.statusBarItem.show();
    }

    /**
     * Oculta la barra de estado
     */
    hide(): void {
        this.statusBarItem.hide();
    }

    /**
     * Actualiza el estado
     */
    async updateStatus(): Promise<void> {
        try {
            const health = await this.apiClient.checkHealth();
            
            if (health.status === 'healthy' && health.ollama === 'connected') {
                // Estado conectado
                this.statusBarItem.text = `$(bot) ${health.model}`;
                this.statusBarItem.color = undefined; // Color por defecto
                this.statusBarItem.tooltip = `IA Local Vargas\nModelo: ${health.model}\nEstado: Conectado`;
            } else if (health.status === 'healthy') {
                // API conectada pero Ollama no
                this.statusBarItem.text = `$(warning) API OK`;
                this.statusBarItem.color = new vscode.ThemeColor('errorForeground');
                this.statusBarItem.tooltip = 'IA Local Vargas\nAPI conectada pero Ollama no está activo';
            } else {
                // Sin conexión
                this.statusBarItem.text = `$(error) IA Offline`;
                this.statusBarItem.color = new vscode.ThemeColor('errorForeground');
                this.statusBarItem.tooltip = 'IA Local Vargas\nAPI desconectada\nInicia api_server.py';
            }
            
        } catch (error) {
            // Error de conexión
            this.statusBarItem.text = `$(error) IA Offline`;
            this.statusBarItem.color = new vscode.ThemeColor('errorForeground');
            this.statusBarItem.tooltip = `IA Local Vargas\nError: ${(error as Error).message}`;
        }
    }

    /**
     * Dispose recursos
     */
    dispose(): void {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        if (this.statusBarItem) {
            this.statusBarItem.dispose();
        }
    }
}

