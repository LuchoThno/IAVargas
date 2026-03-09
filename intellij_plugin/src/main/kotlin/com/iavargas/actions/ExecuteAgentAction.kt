package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.PlatformDataKeys
import com.intellij.openapi.project.Project
import com.iavargas.IaLocalVargasPlugin
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.application.ApplicationManager

/**
 * Accion para ejecutar un agente de ai_dev_system en el codigo seleccionado
 */
class ExecuteAgentAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        val editor = event.getData(PlatformDataKeys.EDITOR) ?: return
        
        val selectionModel = editor.selectionModel
        if (!selectionModel.hasSelection()) {
            IaLocalVargasPlugin.showError(project, "Selecciona codigo para procesar")
            return
        }
        
        val code = selectionModel.selectedText ?: return
        
        try {
            val api = getApi()
            
            // Obtener lista de agentes
            ApplicationManager.getApplication().executeOnPooledThread {
                try {
                    val agents = api.listAgents()
                    
                    if (agents.agents.isEmpty()) {
                        ApplicationManager.getApplication().invokeLater {
                            IaLocalVargasPlugin.showError(project, "No hay agentes disponibles")
                        }
                        return@executeOnPooledThread
                    }
                    
                    // Mostrar dialogo para seleccionar agente
                    ApplicationManager.getApplication().invokeLater {
                        val selectedAgent = Messages.showChooseDialog(
                            project,
                            "Selecciona el agente a ejecutar",
                            "Ejecutar Agente - IA Vargas",
                            Messages.getQuestionIcon(),
                            agents.agents.toTypedArray(),
                            agents.agents.firstOrNull() ?: ""
                        )
                        
                        if (selectedAgent.isNullOrBlank()) {
                            return@invokeLater
                        }
                        
                        // Ejecutar agente
                        executeAgent(project, code, selectedAgent)
                    }
                    
                } catch (e: Exception) {
                    ApplicationManager.getApplication().invokeLater {
                        IaLocalVargasPlugin.showError(project, "Error: ${e.message}")
                    }
                }
            }
            
        } catch (e: Exception) {
            IaLocalVargasPlugin.showError(project, "Error: ${e.message}")
        }
    }
    
    private fun executeAgent(project: Project, code: String, agent: String) {
        val api = getApi()
        
        ApplicationManager.getApplication().executeOnPooledThread {
            try {
                val result = api.executeAgentCommand(agent, code)
                
                ApplicationManager.getApplication().invokeLater {
                    // Mostrar resultado
                    val tempFile = com.intellij.openapi.fileEditor.impl.OpenFileDescriptor(
                        project,
                        project.basePath?.let { java.io.File(it, "agent_result.txt") } 
                            ?: java.io.File("agent_result.txt")
                    )
                    
                    // Reemplazar seleccion con resultado
                    IaLocalVargasPlugin.replaceSelection(project, result)
                    
                    Messages.showMessageDialog(
                        project,
                        "Agente '$agent' ejecutado. Resultado insertado en el editor.",
                        "Agente Ejecutado",
                        Messages.getInformationIcon()
                    )
                }
                
            } catch (e: Exception) {
                ApplicationManager.getApplication().invokeLater {
                    IaLocalVargasPlugin.showError(project, "Error: ${e.message}")
                }
            }
        }
    }
    
    private fun getApi() = IaLocalVargasPlugin.api
}

