"use strict";
/**
 * StatusBar - Barra de Estado
 * ========================
 * Muestra el estado de la IA en la barra de estado de VSCode
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
exports.IaLocalVargasStatusBar = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Manejador de la barra de estado
 */
class IaLocalVargasStatusBar {
    statusBarItem;
    apiClient;
    updateInterval = null;
    constructor(apiClient) {
        this.apiClient = apiClient;
        // Crear elemento de barra de estado
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
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
    show() {
        this.statusBarItem.show();
    }
    /**
     * Oculta la barra de estado
     */
    hide() {
        this.statusBarItem.hide();
    }
    /**
     * Actualiza el estado
     */
    async updateStatus() {
        try {
            const health = await this.apiClient.checkHealth();
            if (health.status === 'healthy' && health.ollama === 'connected') {
                // Estado conectado
                this.statusBarItem.text = `$(bot) ${health.model}`;
                this.statusBarItem.color = undefined; // Color por defecto
                this.statusBarItem.tooltip = `IA Local Vargas\nModelo: ${health.model}\nEstado: Conectado`;
            }
            else if (health.status === 'healthy') {
                // API conectada pero Ollama no
                this.statusBarItem.text = `$(warning) API OK`;
                this.statusBarItem.color = new vscode.ThemeColor('errorForeground');
                this.statusBarItem.tooltip = 'IA Local Vargas\nAPI conectada pero Ollama no está activo';
            }
            else {
                // Sin conexión
                this.statusBarItem.text = `$(error) IA Offline`;
                this.statusBarItem.color = new vscode.ThemeColor('errorForeground');
                this.statusBarItem.tooltip = 'IA Local Vargas\nAPI desconectada\nInicia api_server.py';
            }
        }
        catch (error) {
            // Error de conexión
            this.statusBarItem.text = `$(error) IA Offline`;
            this.statusBarItem.color = new vscode.ThemeColor('errorForeground');
            this.statusBarItem.tooltip = `IA Local Vargas\nError: ${error.message}`;
        }
    }
    /**
     * Dispose recursos
     */
    dispose() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        if (this.statusBarItem) {
            this.statusBarItem.dispose();
        }
    }
}
exports.IaLocalVargasStatusBar = IaLocalVargasStatusBar;
//# sourceMappingURL=statusBar.js.map