package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.PlatformDataKeys
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.iavargas.IaLocalVargasPlugin

/**
 * Acción para depurar código
 */
class DebugAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        val editor = event.getData(PlatformDataKeys.EDITOR) ?: return
        
        val selectionModel = editor.selectionModel
        if (!selectionModel.hasSelection()) {
            IaLocalVargasPlugin.showError(project, "Selecciona código para depurar")
            return
        }
        
        val code = selectionModel.selectedText ?: return
        val language = getLanguage(editor)
        
        try {
            val api = getApi()
            val result = api.debug(code, language)
            
            // Mostrar diff y preguntar si aplicar
            val apply = Messages.showYesNoDialog(
                project,
                "¿Aplicar corrección?",
                "Depuración",
                "Aplicar",
                "Cancelar",
                Messages.getQuestionIcon()
            )
            
            if (apply == Messages.YES) {
                replaceSelection(project, editor, result)
                IaLocalVargasPlugin.showInfo(project, "✅ Código corregido")
            }
            
        } catch (e: Exception) {
            IaLocalVargasPlugin.showError(project, "Error: ${e.message}")
        }
    }
    
    private fun getApi() = IaLocalVargasPlugin.api
    
    private fun getLanguage(editor: Editor): String {
        val file = editor.document.psiFile
        return when (file?.language?.id) {
            "Python" -> "python"
            "Java" -> "java"
            else -> "python"
        }
    }
    
    private fun replaceSelection(project: Project, editor: Editor, text: String) {
        com.intellij.openapi.command.WriteCommandAction.runWriteCommandAction(project) {
            editor.selectionModel.replaceSelection(text)
        }
    }
}

