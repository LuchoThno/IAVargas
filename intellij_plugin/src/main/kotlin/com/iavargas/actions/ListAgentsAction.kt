package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.iavargas.IaLocalVargasPlugin
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.application.ApplicationManager

/**
 * Accion para listar los agentes disponibles de ai_dev_system
 */
class ListAgentsAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        
        try {
            val api = getApi()
            
            ApplicationManager.getApplication().executeOnPooledThread {
                try {
                    val agents = api.listAgents()
                    
                    ApplicationManager.getApplication().invokeLater {
                        val message = buildString {
                            appendLine("Agentes Disponibles")
                            appendLine("====================")
                            appendLine()
                            appendLine("Total: ${agents.count}")
                            appendLine()
                            
                            agents.agents.forEach { agent ->
                                appendLine("- $agent")
                            }
                            
                            appendLine()
                            appendLine("Uso: Selecciona codigo y usa 'Ejecutar Agente'")
                        }
                        
                        Messages.showMessageDialog(
                            project,
                            message,
                            "Agentes - IA Vargas",
                            Messages.getInformationIcon()
                        )
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
    
    private fun getApi() = IaLocalVargasPlugin.api
}

