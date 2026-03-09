package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.PlatformDataKeys
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.iavargas.IaLocalVargasPlugin
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.application.ApplicationManager

/**
 * Acción para explicar código
 */
class ExplainAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        val editor = event.getData(PlatformDataKeys.EDITOR) ?: return
        
        val selectionModel = editor.selectionModel
        if (!selectionModel.hasSelection()) {
            IaLocalVargasPlugin.showError(project, "Selecciona código para explicar")
            return
        }
        
        val code = selectionModel.selectedText ?: return
        
        try {
            val api = getApi()
            val explanation = api.ask(
                "Explica este código de forma clara y simple:\n\n$code",
                temperature = 0.5,
                maxTokens = 1500
            )
            
            // Mostrar en diálogo
            ApplicationManager.getApplication().invokeLater {
                Messages.showMessageDialog(
                    project,
                    explanation,
                    "Explicación de Código",
                    Messages.getInformationIcon()
                )
            }
            
        } catch (e: Exception) {
            IaLocalVargasPlugin.showError(project, "Error: ${e.message}")
        }
    }
    
    private fun getApi() = IaLocalVargasPlugin.api
}

