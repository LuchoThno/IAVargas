package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.PlatformDataKeys
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.iavargas.IaLocalVargasPlugin
import com.iavargas.api.IaLocalVargasApi

/**
 * Acción para analizar código
 */
class AnalyzeAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        val editor = event.getData(PlatformDataKeys.EDITOR) ?: return
        
        // Obtener código seleccionado o todo el archivo
        val code = getSelectedOrAllCode(editor) ?: run {
            IaLocalVargasPlugin.showError(project, "No hay código para analizar")
            return
        }
        
        // Obtener lenguaje
        val language = getLanguage(editor)
        
        // Ejecutar análisis
        try {
            val api = getApi()
            val result = api.analyze(code, language)
            
            // Mostrar resultados
            val message = buildString {
                appendLine("📊 Análisis de Código")
                appendLine("─────────────────")
                appendLine("Líneas: ${result.lines}")
                appendLine("Puntuación: ${result.score}/100")
                appendLine()
                
                if (result.securityIssues.isNotEmpty()) {
                    appendLine("⚠️ Problemas de Seguridad:")
                    result.securityIssues.forEach { issue ->
                        appendLine("  - ${issue.message}")
                    }
                    appendLine()
                }
                
                appendLine("📈 Complejidad:")
                appendLine("  - Ciclomática: ${result.complexity.cyclomatic}")
                appendLine("  - Funciones: ${result.complexity.functions}")
                appendLine("  - Clases: ${result.complexity.classes}")
                appendLine()
                
                if (result.suggestions.isNotEmpty()) {
                    appendLine("💡 Sugerencias:")
                    result.suggestions.take(5).forEach { suggestion ->
                        appendLine("  - $suggestion")
                    }
                }
            }
            
            IaLocalVargasPlugin.showInfo(project, message)
            
        } catch (e: Exception) {
            IaLocalVargasPlugin.showError(project, "Error: ${e.message}")
        }
    }
    
    private fun getSelectedOrAllCode(editor: Editor): String? {
        val selectionModel = editor.selectionModel
        return if (selectionModel.hasSelection()) {
            selectionModel.selectedText
        } else {
            editor.document.text
        }
    }
    
    private fun getLanguage(editor: Editor): String {
        val file = editor.document.psiFile
        return when (file?.language?.id) {
            "Python" -> "python"
            "Java" -> "java"
            "JavaScript" -> "javascript"
            "TypeScript" -> "typescript"
            "Kotlin" -> "kotlin"
            "Go" -> "go"
            "Rust" -> "rust"
            "C" -> "c"
            "CPP" -> "cpp"
            else -> "python"
        }
    }
    
    private fun getApi(): IaLocalVargasApi {
        return IaLocalVargasPlugin.api
    }
}

