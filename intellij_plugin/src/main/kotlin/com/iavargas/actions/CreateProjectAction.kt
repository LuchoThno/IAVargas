package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.iavargas.IaLocalVargasPlugin
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.application.ApplicationManager

/**
 * Accion para crear un proyecto completo usando ai_dev_system
 */
class CreateProjectAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        
        try {
            // Pedir descripcion del proyecto
            val description = Messages.showInputDialog(
                project,
                "Describe el proyecto que quieres crear",
                "Crear Proyecto - IA Vargas",
                Messages.getQuestionIcon()
            )
            
            if (description.isNullOrBlank()) {
                return
            }
            
            // Pedir lenguaje
            val language = Messages.showEditableChooseDialog(
                "Selecciona el lenguaje",
                "Lenguaje de Programacion",
                Messages.getQuestionIcon(),
                arrayOf("python", "javascript", "typescript", "java", "go", "rust"),
                "python",
                null
            )
            
            if (language.isNullOrBlank()) {
                return
            }
            
            // Mostrar progreso
            val api = getApi()
            
            ApplicationManager.getApplication().executeOnPooledThread {
                try {
                    val result = api.createProject(description, language)
                    
                    ApplicationManager.getApplication().invokeLater {
                        val message = buildString {
                            appendLine("Proyecto Creado")
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
                            }
                        }
                        
                        Messages.showMessageDialog(
                            project,
                            message,
                            "Proyecto Creado - IA Vargas",
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

