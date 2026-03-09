package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.iavargas.IaLocalVargasPlugin
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.application.ApplicationManager

/**
 * Accion para orquestar una tarea compleja usando ai_dev_system
 */
class OrchestrateAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        
        try {
            // Pedir descripcion de la tarea
            val task = Messages.showInputDialog(
                project,
                "Describe la tarea que quieres que la IA realice",
                "Orquestar Tarea - IA Vargas",
                Messages.getQuestionIcon()
            )
            
            if (task.isNullOrBlank()) {
                return
            }
            
            // Mostrar progreso
            val api = getApi()
            
            ApplicationManager.getApplication().executeOnPooledThread {
                try {
                    val result = api.orchestrate(task)
                    
                    ApplicationManager.getApplication().invokeLater {
                        val message = buildString {
                            appendLine("Tarea Completada")
                            appendLine("===============")
                            appendLine()
                            appendLine("Estado: ${result.status}")
                            appendLine("Iteraciones: ${result.iterations}")
                            appendLine()
                            
                            if (result.output.isNotBlank()) {
                                appendLine("Salida:")
                                appendLine(result.output)
                                appendLine()
                            }
                            
                            if (result.error.isNotBlank()) {
                                appendLine("Errores:")
                                appendLine(result.error)
                                appendLine()
                            }
                            
                            if (result.history.isNotEmpty()) {
                                appendLine("Historial:")
                                result.history.take(15).forEach { h ->
                                    appendLine("- $h")
                                }
                            }
                        }
                        
                        Messages.showMessageDialog(
                            project,
                            message,
                            "Orquestacion - IA Vargas",
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

