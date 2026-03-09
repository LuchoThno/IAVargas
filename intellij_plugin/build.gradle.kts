plugins {
    id("java")
    id("org.jetbrains.intellij") version "1.17.4"
    id("org.jetbrains.kotlin.jvm") version "1.9.22"
}

group = "com.iavargas"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // IntelliJ Platform
    implementation("org.jetbrains.intellij:gradle-intellij-plugin:1.17.4")
    
    // Kotlin
    implementation(kotlin("stdlib"))
    
    // HTTP Client
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    
    // JSON
    implementation("com.google.code.gson:gson:2.10.1")
    
    // Testing
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.10.1")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.10.1")
}

// Configure IntelliJ plugin
intellij {
    pluginName.set("IA Local Vargas")
    version.set("2023.3")
    type.set("IC") // IntelliJ IDEA Community
    
    // Plugins to include
    plugins.set(listOf(
        "com.intellij.modules.lang",
        "com.intellij.modules.python",
        "com.intellij.modules.java"
    ))
}

tasks {
    // Build plugin
    buildPlugin {
        dependsOn("patchPluginXml")
    }
    
    // Run IDE
    runIde {
        // Run with the plugin
    }
    
    // Test
    test {
        useJUnitPlatform()
    }
    
    // Patch plugin.xml
    patchPluginXml {
        pluginDescription.set("""
            Asistente de IA local para programadores
            
            Características:
            - Chat con IA
            - Análisis de código
            - Refactorización
            - Generación de tests
            - Depuración
            - Optimización
        """.trimIndent())
        
        // Changeable variables
        pluginVersion.set(project.version.toString())
        
        // IDE compatibility
        ideaVersion.set(
            org.jetbrains.intellij.gradle.utils.IdeaVersion("2023.3", "IC")
        )
    }
}

// Kotlin configuration
kotlin {
    jvmToolchain(17)
}

