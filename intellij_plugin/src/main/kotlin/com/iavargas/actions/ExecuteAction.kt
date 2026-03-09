package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.PlatformDataKeys
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.iavargas.IaLocalVargasPlugin

/**
 * Acción para ejecutar código
 */
class ExecuteAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        val editor = event.getData(PlatformDataKeys.EDITOR) ?: return
        
        val selectionModel = editor.selectionModel
        if (!selectionModel.hasSelection()) {
            IaLocalVargasPlugin.showError(project, "Selecciona código para ejecutar")
            return
        }
        
        val code = selectionModel.selectedText ?: return
        val language = getLanguage(editor)
        
        try {
            val api = getApi()
            val result = api.execute(code, language, timeout = 30)
            
            // Mostrar resultado
            val message = buildString {
                appendLine("🚀 Ejecución ($language)")
                appendLine("─────────────────")
                appendLine(if (result.success) "✅ Éxito" else "❌ Error")
                appendLine()
                
                if (result.stdout.isNotEmpty()) {
                    appendLine("📤 Salida:")
                    appendLine(result.stdout)
                }
                
                if (result.stderr.isNotEmpty()) {
                    appendLine()
                    appendLine("⚠️ Error:")
                    appendLine(result.stderr)
                }
            }
            
            Messages.showMessageDialog(
                project,
                message,
                "Resultado de Ejecución",
                if (result.success) Messages.getInformationIcon() else Messages.getErrorIcon()
            )
            
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
            "JavaScript" -> "javascript"
            "Kotlin" -> "kotlin"
            else -> "python"
        }
    }
}

