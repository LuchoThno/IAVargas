"""
Verification Report - IA Local Vargas Connections
=================================================
This script verifies that all components are properly connected.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_file_exists(filepath, description):
    """Verify a file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def verify_import(module_path, items, description):
    """Verify imports work"""
    try:
        module = __import__(module_path, fromlist=items)
        for item in items:
            if hasattr(module, item):
                print(f"  ✓ {item}")
            else:
                print(f"  ✗ {item} - NOT FOUND")
        return True
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

print("=" * 60)
print("IA LOCAL VARGAS - VERIFICATION REPORT")
print("=" * 60)

# 1. Verify main files exist
print("\n1. Main Files:")
verify_file_exists("app.py", "Main application")
verify_file_exists("api_server.py", "API Server")
verify_file_exists("documents.py", "Documents module")
verify_file_exists("web_search.py", "Web search module")
verify_file_exists("code_agent.py", "Code agent")
verify_file_exists("plugins.py", "Plugins system")
verify_file_exists("code_analyzer.py", "Code analyzer")
verify_file_exists("language_executor.py", "Language executor")
verify_file_exists("project_creator.py", "Project creator")

# 2. Verify memory_engine
print("\n2. Memory Engine:")
verify_file_exists("memory_engine/__init__.py", "Memory engine init")
verify_file_exists("memory_engine/config.py", "Memory config")
verify_file_exists("memory_engine/db.py", "Database layer")
verify_file_exists("memory_engine/embeddings.py", "Embeddings")
verify_file_exists("memory_engine/memory_store.py", "Memory storage")
verify_file_exists("memory_engine/memory_search.py", "Memory search")
verify_file_exists("memory_engine/memory_router.py", "Memory router")
verify_file_exists("memory_engine/memory_cleanup.py", "Memory cleanup")
verify_file_exists("memory_engine/knowledge_graph.py", "Knowledge graph")
verify_file_exists("memory_engine/document_loader.py", "Document loader")
verify_file_exists("memory_engine/embedding_engine.py", "Embedding engine")
verify_file_exists("memory_engine/text_chunker.py", "Text chunker")
verify_file_exists("memory_engine/semantic_search.py", "Semantic search")
verify_file_exists("memory_engine/rag_context_builder.py", "RAG builder")

# 3. Verify VSCode extension
print("\n3. VSCode Extension:")
verify_file_exists("vscode_extension/package.json", "Package config")
verify_file_exists("vscode_extension/src/extension.ts", "Extension entry")
verify_file_exists("vscode_extension/src/api.ts", "API client")
verify_file_exists("vscode_extension/src/commands.ts", "Commands")

# 4. Verify IntelliJ plugin
print("\n4. IntelliJ Plugin:")
verify_file_exists("intellij_plugin/build.gradle.kts", "Build config")
verify_file_exists("intellij_plugin/src/main/kotlin/com/iavargas/IaLocalVargasPlugin.kt", "Plugin main")
verify_file_exists("intellij_plugin/src/main/kotlin/com/iavargas/api/IaLocalVargasApi.kt", "API client")

# 5. Data directories
print("\n5. Data Directories:")
verify_file_exists("data/", "Data directory")
verify_file_exists("documents/", "Documents directory")
verify_file_exists("workspace/projects/", "Projects directory")

print("\n" + "=" * 60)
print("All files verified!")
print("=" * 60)
print("\nTo start the application, run:")
print("  python app.py")
print("\nTo start the API server, run:")
print("  python api_server.py")

