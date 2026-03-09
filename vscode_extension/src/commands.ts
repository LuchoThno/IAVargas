/**
 * Commands - Comandos de VSCode
 * ============================
 * Registra todos los comandos disponibles para la extension
 */

import * as vscode from 'vscode';
import { ApiClient } from './api';
import { ExtensionConfig } from './config';
import { IaLocalVargasPanel } from './panel';

/**
 * Registra todos los comandos de la extension
 */
export function registerCommands(
    context: vscode.ExtensionContext,
    apiClient: ApiClient,
    config: ExtensionConfig
): void {
    // Comando: Preguntar a la IA
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.ask', async () => {
            try {
                const question = await vscode.window.showInputBox({
                    prompt: 'Que quieres preguntar a la IA?',
                    placeHolder: 'Escribe tu pregunta...',
                    ignoreFocusOut: true
                });

                if (!question) { return; }

                const answer = await apiClient.ask({
                    prompt: question,
                    temperature: config.temperature,
                    max_tokens: config.maxTokens
                });

                if (config.showNotifications) {
                    const selectedAction = await vscode.window.showInformationMessage(
                        'Que deseas hacer con la respuesta?',
                        { modal: true },
                        'Copiar al portapapeles',
                        'Mostrar en panel'
                    );

                    if (selectedAction === 'Copiar al portapapeles') {
                        await vscode.env.clipboard.writeText(answer);
                        vscode.window.showInformationMessage('Copiado al portapapeles');
                    } else if (selectedAction === 'Mostrar en panel') {
                        IaLocalVargasPanel.createOrShow(context.extensionUri, apiClient);
                        IaLocalVargasPanel.addMessage('user', question);
                        IaLocalVargasPanel.addMessage('assistant', answer);
                    }
                }

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Analizar codigo
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.analyze', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para analizar');
                    return;
                }

                const language = ExtensionConfig.getCurrentLanguage();
                
                const outputChannel = vscode.window.createOutputChannel('IA Vargas - Analisis');
                outputChannel.appendLine('Analizando codigo...');
                outputChannel.show();

                const result = await apiClient.analyze({
                    code,
                    language,
                    include_security: true,
                    include_complexity: true
                });

                let message = `Analisis de Codigo (${language})\n\n`;
                message += `Lineas: ${result.lines}\n`;
                message += `Puntuacion: ${result.score}/100\n\n`;

                if (result.security_issues.length > 0) {
                    message += `Problemas de Seguridad (${result.security_issues.length}):\n`;
                    result.security_issues.forEach(issue => {
                        message += `- ${issue.message}\n`;
                    });
                    message += '\n';
                }

                if (result.complexity) {
                    message += `Complejidad:\n`;
                    message += `- Complejidad ciclamatica: ${result.complexity.cyclomatic}\n`;
                    message += `- Funciones: ${result.complexity.functions}\n`;
                    message += `- Clases: ${result.complexity.classes}\n\n`;
                }

                if (result.suggestions.length > 0) {
                    message += `Sugerencias:\n`;
                    result.suggestions.slice(0, 5).forEach(s => {
                        message += `- ${s}\n`;
                    });
                }

                outputChannel.appendLine(message);
                vscode.window.showInformationMessage('Analisis completado');

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Refactorizar
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.refactor', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para refactorizar');
                    return;
                }

                const language = ExtensionConfig.getCurrentLanguage();

                const result = await apiClient.refactor({
                    code,
                    language,
                    style: 'default'
                });

                await showDiff(code, result, 'Refactorizacion');

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Generar tests
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.test', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para generar tests');
                    return;
                }

                const language = ExtensionConfig.getCurrentLanguage();

                const tests = await apiClient.generateTests({
                    code,
                    language,
                    framework: 'pytest',
                    test_count: 3
                });

                const testFileName = await vscode.window.showInputBox({
                    prompt: 'Nombre del archivo de tests',
                    value: 'test_generated.py',
                    ignoreFocusOut: true
                });

                if (testFileName) {
                    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
                    if (workspaceFolder) {
                        const testPath = vscode.Uri.joinPath(
                            workspaceFolder.uri,
                            testFileName
                        );
                        
                        await vscode.workspace.fs.writeFile(
                            testPath,
                            Buffer.from(tests, 'utf-8')
                        );
                        
                        const doc = await vscode.workspace.openTextDocument(testPath);
                        await vscode.window.showTextDocument(doc);
                        
                        vscode.window.showInformationMessage('Tests generados');
                    }
                }

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Depurar
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.debug', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para depurar');
                    return;
                }

                const language = ExtensionConfig.getCurrentLanguage();

                const result = await apiClient.debug({
                    code,
                    language
                });

                await showDiff(code, result, 'Depuracion');

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Optimizar
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.optimize', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para optimizar');
                    return;
                }

                const language = ExtensionConfig.getCurrentLanguage();

                const result = await apiClient.optimize({
                    code,
                    language,
                    focus: 'performance'
                });

                await showDiff(code, result, 'Optimizacion');

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Generar codigo
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.generate', async () => {
            try {
                const description = await vscode.window.showInputBox({
                    prompt: 'Describe el codigo que quieres generar',
                    placeHolder: 'Ej: una funcion que calcule el factorial',
                    ignoreFocusOut: true
                });

                if (!description) { return; }

                const language = ExtensionConfig.getCurrentLanguage();

                const result = await apiClient.generate({
                    description,
                    language
                });

                const editor = vscode.window.activeTextEditor;
                if (editor) {
                    await editor.edit(editBuilder => {
                        editBuilder.insert(editor.selection.end, '\n\n' + result);
                    });
                }

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Explicar codigo
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.explain', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para explicar');
                    return;
                }

                const explanation = await apiClient.ask({
                    prompt: `Explica este codigo de forma clara y simple:\n\n${code}`,
                    temperature: 0.5,
                    max_tokens: 1000
                });

                const doc = await vscode.workspace.openTextDocument({
                    content: `# Explicacion de Codigo\n\n${explanation}`,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Ejecutar codigo
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.execute', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para ejecutar');
                    return;
                }

                const language = ExtensionConfig.getCurrentLanguage();

                const outputChannel = vscode.window.createOutputChannel('IA Vargas - Ejecucion');
                outputChannel.appendLine(`Ejecutando codigo ${language}...`);
                outputChannel.show();

                const result = await apiClient.execute({
                    code,
                    language,
                    timeout: 30
                });

                if (result.stdout) {
                    outputChannel.appendLine(`\nSalida:\n${result.stdout}`);
                }
                
                if (result.stderr) {
                    outputChannel.appendLine(`\nError:\n${result.stderr}`);
                }

                if (result.success) {
                    outputChannel.appendLine('\nEjecucion exitosa');
                }

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Mostrar panel
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.showPanel', () => {
            IaLocalVargasPanel.createOrShow(context.extensionUri, apiClient);
        })
    );

    // Comando: Estado del sistema
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.status', async () => {
            try {
                const health = await apiClient.checkHealth();

                const status = `
IA Local Vargas - Estado

| Componente | Estado |
|------------|--------|
| API | ${health.status === 'healthy' ? 'Conectada' : 'Desconectada'} |
| Ollama | ${health.ollama === 'connected' ? 'Activo' : 'Inactivo'} |
| ai_dev_system | ${(health as any).ai_dev_system ? 'Disponible' : 'No disponible'} |
| Modelo | ${health.model} |

${health.available_models.length > 0 
    ? `Modelos disponibles:\n${health.available_models.map(m => `- ${m}`).join('\n')}`
    : 'No hay modelos disponibles'}
                `;

                const doc = await vscode.workspace.openTextDocument({
                    content: status,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // ============================================
    // COMANDOS ai_dev_system
    // ============================================

    // Comando: Crear proyecto
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.createProject', async () => {
            try {
                const description = await vscode.window.showInputBox({
                    prompt: 'Describe el proyecto que quieres crear',
                    placeHolder: 'Ej: una aplicacion web con Flask',
                    ignoreFocusOut: true
                });

                if (!description) { return; }

                const language = await vscode.window.showQuickPick(
                    ['python', 'javascript', 'typescript', 'java', 'go', 'rust'],
                    { placeHolder: 'Selecciona el lenguaje' }
                );

                if (!language) { return; }

                const outputChannel = vscode.window.createOutputChannel('IA Vargas - Crear Proyecto');
                outputChannel.appendLine(`Creando proyecto: ${description}`);
                outputChannel.appendLine(`Lenguaje: ${language}`);
                outputChannel.show();

                const result = await apiClient.createProject({
                    description,
                    language
                });

                let message = `# Proyecto Creado\n\n`;
                message += `Estado: ${result.status}\n`;
                message += `Iteraciones: ${result.iterations}\n\n`;

                if (result.output) {
                    message += `Salida:\n${result.output}\n`;
                }

                if (result.error) {
                    message += `Errores:\n${result.error}\n`;
                }

                outputChannel.appendLine(message);

                const doc = await vscode.workspace.openTextDocument({
                    content: message,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Orquestar tarea
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.orchestrate', async () => {
            try {
                const task = await vscode.window.showInputBox({
                    prompt: 'Describe la tarea que quieres que la IA realice',
                    placeHolder: 'Ej: crear un sistema de gestion de tareas',
                    ignoreFocusOut: true
                });

                if (!task) { return; }

                const outputChannel = vscode.window.createOutputChannel('IA Vargas - Orquestar');
                outputChannel.appendLine(`Orquestando tarea: ${task}`);
                outputChannel.show();

                const result = await apiClient.orchestrate({
                    task,
                    max_iterations: 10
                });

                let message = `# Tarea Completada\n\n`;
                message += `Estado: ${result.status}\n`;
                message += `Iteraciones: ${result.iterations}\n\n`;

                if (result.output) {
                    message += `Salida:\n${result.output}\n`;
                }

                if (result.error) {
                    message += `Errores:\n${result.error}\n`;
                }

                if (result.history && result.history.length > 0) {
                    message += `Historial:\n`;
                    result.history.slice(0, 15).forEach((h: string) => {
                        message += `- ${h}\n`;
                    });
                }

                outputChannel.appendLine(message);

                const doc = await vscode.workspace.openTextDocument({
                    content: message,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Listar agentes
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.listAgents', async () => {
            try {
                const agents = await apiClient.listAgents();

                let message = `# Agentes Disponibles\n\n`;
                message += `Total: ${agents.count}\n\n`;
                
                agents.agents.forEach(agent => {
                    message += `- ${agent}\n`;
                });

                const doc = await vscode.workspace.openTextDocument({
                    content: message,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );

    // Comando: Ejecutar agente
    context.subscriptions.push(
        vscode.commands.registerCommand('iaLocalVargas.executeAgent', async () => {
            try {
                const code = ExtensionConfig.getSelectedCode();
                if (!code) {
                    vscode.window.showWarningMessage('Selecciona codigo para procesar');
                    return;
                }

                const agents = await apiClient.listAgents();
                
                const selectedAgent = await vscode.window.showQuickPick(
                    agents.agents,
                    { placeHolder: 'Selecciona el agente a ejecutar' }
                );

                if (!selectedAgent) { return; }

                const result = await apiClient.executeAgentCommand(
                    selectedAgent,
                    code
                );

                await showDiff(code, result, `Agente: ${selectedAgent}`);

            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${(error as Error).message}`);
            }
        })
    );
}

/**
 * Muestra un diff entre el codigo original y el modificado
 */
async function showDiff(_original: string, modified: string, title: string): Promise<void> {
    const tempDoc = await vscode.workspace.openTextDocument({
        content: modified,
        language: ExtensionConfig.getCurrentLanguage()
    });
    
    await vscode.window.showTextDocument(tempDoc, {
        viewColumn: vscode.ViewColumn.Beside,
        preserveFocus: true
    });

    const apply = await vscode.window.showInformationMessage(
        `Aplicar cambios de ${title}?`,
        { modal: true },
        'Aplicar',
        'Cancelar'
    );

    if (apply === 'Aplicar') {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            await editor.edit(editBuilder => {
                const selection = editor.selection;
                editBuilder.replace(selection, modified);
            });
        }
    }
}

