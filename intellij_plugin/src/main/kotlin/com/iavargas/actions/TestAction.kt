package com.iavargas.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.PlatformDataKeys
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.LocalFileSystem
import com.iavargas.IaLocalVargasPlugin
import java.io.File

/**
 * Acción para generar tests
 */
class TestAction : AnAction() {
    
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project ?: return
        val editor = event.getData(PlatformDataKeys.EDITOR) ?: return
        
        val selectionModel = editor.selectionModel
        if (!selectionModel.hasSelection()) {
            IaLocalVargasPlugin.showError(project, "Selecciona código para generar tests")
            return
        }
        
        val code = selectionModel.selectedText ?: return
        val language = getLanguage(editor)
        
        try {
            val api = getApi()
            val tests = api.generateTests(code, language)
            
            // Crear archivo de test
            val testFileName = "TestGenerated.kt"
            val basePath = project.basePath ?: return
            val testFile = File("$basePath/$testFileName")
            
            testFile.writeText(tests)
            
            // Refrescar y abrir archivo
            val vfs = LocalFileSystem.getInstance()
            val virtualFile = vfs.findFileByPath(testFile.absolutePath)
            
            if (virtualFile != null) {
                com.intellij.openapi.fileEditor.FileEditorManager.getInstance(project)
                    .openFile(virtualFile, true)
            }
            
            IaLocalVargasPlugin.showInfo(project, "✅ Tests generados en $testFileName")
            
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

