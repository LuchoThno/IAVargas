package com.iavargas.config

import com.intellij.openapi.components.*
import com.intellij.openapi.project.Project

/**
 * Configuración del plugin
 */
@State(
    name = "IaLocalVargasSettings",
    storages = [Storage("ia_local_vargas.xml")]
)
class PluginSettings : PersistentStateComponent<PluginSettings.State> {
    
    data class State(
        var apiUrl: String = "http://localhost:8000",
        var model: String = "llama3",
        var temperature: Double = 0.7,
        var maxTokens: Int = 2048,
        var showNotifications: Boolean = true,
        var autoExecute: Boolean = false
    )
    
    var state = State()
    
    override fun getState(): State = state
    
    override fun loadState(state: State) {
        this.state = state
    }
    
    companion object {
        fun getInstance(): PluginSettings {
            return service()
        }
        
        fun getInstance(project: Project): PluginSettings {
            return project.getService(PluginSettings::class.java)
        }
    }
}

/**
 * Proveedor de configurable para UI de Settings
 */
class IaLocalVargasConfigurable : Configurable {
    
    private var settingsComponent: SettingsComponent? = null
    
    override fun getDisplayName(): String = "IA Local Vargas"
    
    override fun createComponent(): javax.swing.JComponent {
        settingsComponent = SettingsComponent()
        return settingsComponent!!.panel
    }
    
    override fun isModified(): Boolean {
        val settings = PluginSettings.getInstance()
        return settingsComponent?.let {
            it.apiUrl != settings.state.apiUrl ||
            it.model != settings.state.model ||
            it.temperature != settings.state.temperature ||
            it.maxTokens != settings.state.maxTokens ||
            it.showNotifications != settings.state.showNotifications ||
            it.autoExecute != settings.state.autoExecute
        } ?: false
    }
    
    override fun apply() {
        val settings = PluginSettings.getInstance()
        settingsComponent?.let {
            settings.state.apiUrl = it.apiUrl
            settings.state.model = it.model
            settings.state.temperature = it.temperature
            settings.state.maxTokens = it.maxTokens
            settings.state.showNotifications = it.showNotifications
            settings.state.autoExecute = it.autoExecute
        }
    }
    
    override fun disposeUIResources() {
        settingsComponent = null
    }
}

/**
 * Componente de UI para configuración
 */
class SettingsComponent {
    
    val panel: javax.swing.JPanel
    
    var apiUrl: String
        get() = apiUrlField.text
        set(value) { apiUrlField.text = value }
    
    var model: String
        get() = modelField.text
        set(value) { modelField.text = value }
    
    var temperature: Double
        get() = temperatureSpinner.value as Double
        set(value) { temperatureSpinner.value = value }
    
    var maxTokens: Int
        get() = maxTokensSpinner.value as Int
        set(value) { maxTokensSpinner.value = value }
    
    var showNotifications: Boolean
        get() = notificationsCheck.isSelected
        set(value) { notificationsCheck.isSelected = value }
    
    var autoExecute: Boolean
        get() = autoExecuteCheck.isSelected
        set(value) { autoExecuteCheck.isSelected = value }
    
    private val apiUrlField = javax.swing.JTextField(20).apply {
        text = "http://localhost:8000"
    }
    
    private val modelField = javax.swing.JTextField(20).apply {
        text = "llama3"
    }
    
    private val temperatureSpinner = javax.swing.JSpinner(
        javax.swing.SpinnerNumberModel(0.7, 0.0, 1.0, 0.1)
    )
    
    private val maxTokensSpinner = javax.swing.JSpinner(
        javax.swing.SpinnerNumberModel(2048, 256, 4096, 256)
    )
    
    private val notificationsCheck = javax.swing.JCheckBox("Mostrar notificaciones")
    
    private val autoExecuteCheck = javax.swing.JCheckBox("Auto-ejecutar código generado")
    
    init {
        panel = javax.swing.JPanel().apply {
            layout = java.awt.GridBagLayout()
            border = javax.swing.BorderFactory.createEmptyBorder(10, 10, 10, 10)
            
            val gbc = java.awt.GridBagConstraints().apply {
                insets = java.awt.Insets(5, 5, 5, 5)
                fill = java.awt.GridBagConstraints.HORIZONTAL
                weightx = 1.0
            }
            
            // API URL
            gbc.gridx = 0; gbc.gridy = 0
            add(javax.swing.JLabel("API URL:"), gbc)
            gbc.gridx = 1
            add(apiUrlField, gbc)
            
            // Model
            gbc.gridx = 0; gbc.gridy = 1
            add(javax.swing.JLabel("Modelo:"), gbc)
            gbc.gridx = 1
            add(modelField, gbc)
            
            // Temperature
            gbc.gridx = 0; gbc.gridy = 2
            add(javax.swing.JLabel("Temperature:"), gbc)
            gbc.gridx = 1
            add(temperatureSpinner, gbc)
            
            // Max Tokens
            gbc.gridx = 0; gbc.gridy = 3
            add(javax.swing.JLabel("Max Tokens:"), gbc)
            gbc.gridx = 1
            add(maxTokensSpinner, gbc)
            
            // Notifications
            gbc.gridx = 0; gbc.gridy = 4; gbc.gridwidth = 2
            add(notificationsCheck, gbc)
            
            // Auto Execute
            gbc.gridy = 5
            add(autoExecuteCheck, gbc)
        }
    }
}

