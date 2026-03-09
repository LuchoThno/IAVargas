package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.iavargas.IaLocalVargasPlugin

/**
 * Acción para abrir chat con la IA
 */
class ChatAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        
        // Pedir pregunta al usuario
        val question = Messages.showInputDialog(
            project,
            "Pregunta a la IA:",
            "Chat con IA Local Vargas",
            Messages.getQuestionIcon()
        )
        
        if (question.isNullOrBlank()) return
        
        try {
            val api = getApi()
            val answer = api.ask(question)
            
            // Mostrar respuesta
            Messages.showMessageDialog(
                project,
                answer,
                "Respuesta de IA",
                Messages.getInformationIcon()
            )
            
        } catch (e: Exception) {
            IaLocalVargasPlugin.showError(project, "Error: ${e.message}")
        }
    }
    
    private fun getApi() = IaLocalVargasPlugin.api
}

