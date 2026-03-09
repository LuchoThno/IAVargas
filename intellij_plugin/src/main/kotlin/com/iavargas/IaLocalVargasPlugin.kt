package com.iavargas

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.PlatformDataKeys
import com.intellij.openapi.command.WriteCommandAction
import com.intellij.openapi.editor.Editor
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.iavargas.api.IaLocalVargasApi
import com.iavargas.config.PluginSettings

/**
 * Plugin principal de IA Local Vargas para IntelliJ IDEA
 */
class IaLocalVargasPlugin {
    
    companion object {
        lateinit var api: IaLocalVargasApi
            private set
        
        /**
         * Inicializa el plugin
         */
        fun init() {
            val settings = PluginSettings.getInstance()
            api = IaLocalVargasApi(settings.state.apiUrl, settings.state.model)
        }
        
        /**
         * Obtiene el editor activo
         */
        fun getActiveEditor(event: AnActionEvent): Editor? {
            return event.getData(PlatformDataKeys.EDITOR)
        }
        
        /**
         * Obtiene el proyecto activo
         */
        fun getActiveProject(event: AnActionEvent): Project? {
            return event.project
        }
        
        /**
         * Obtiene el código seleccionado
         */
        fun getSelectedText(event: AnActionEvent): String? {
            val editor = getActiveEditor(event) ?: return null
            val selectionModel = editor.selectionModel
            return if (selectionModel.hasSelection()) {
                selectionModel.selectedText
            } else {
                null
            }
        }
        
        /**
         * Obtiene todo el documento
         */
        fun getDocumentText(event: AnActionEvent): String? {
            val editor = getActiveEditor(event) ?: return null
            return editor.document.text
        }
        
        /**
         * Inserta texto en el editor
         */
        fun insertText(project: Project, text: String) {
            val editor = com.intellij.openapi.editor.LogicalEditorPosition.getEditor(project) ?: return
            
            WriteCommandAction.runWriteCommandAction(project) {
                val caret = editor.caretModel.primaryCaret
                caret.insertText(text)
            }
        }
        
        /**
         * Reemplaza la selección
         */
        fun replaceSelection(project: Project, text: String) {
            val editor = com.intellij.openapi.editor.LogicalEditorPosition.getEditor(project) ?: return
            
            WriteCommandAction.runWriteCommandAction(project) {
                val selectionModel = editor.selectionModel
                if (selectionModel.hasSelection()) {
                    selectionModel.replaceSelection(text)
                } else {
                    editor.caretModel.primaryCaret.insertText(text)
                }
            }
        }
        
        /**
         * Muestra un mensaje de error
         */
        fun showError(project: Project?, message: String) {
            Messages.showMessageDialog(
                project,
                message,
                "Error - IA Local Vargas",
                Messages.getErrorIcon()
            )
        }
        
        /**
         * Muestra un mensaje de información
         */
        fun showInfo(project: Project?, message: String) {
            Messages.showMessageDialog(
                project,
                message,
                "IA Local Vargas",
                Messages.getInformationIcon()
            )
        }
        
        /**
         * Muestra un diálogo de entrada
         */
        fun showInputDialog(project: Project?, title: String, message: String): String? {
            return Messages.showInputDialog(
                project,
                message,
                title,
                Messages.getQuestionIcon()
            )
        }
    }
}

/**
 * Acción base para todas las acciones del plugin
 */
abstract class IaLocalVargasAction : AnAction() {
    
    protected fun getApi(): IaLocalVargasApi = IaLocalVargasPlugin.api
    
    protected fun getSettings() = PluginSettings.getInstance()
    
    protected fun isConnected(): Boolean {
        return try {
            IaLocalVargasPlugin.api.health().isConnected
        } catch (e: Exception) {
            false
        }
    }
}

