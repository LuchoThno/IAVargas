"""
Context Builder - Provides relevant context to LLM
=================================================
Builds context from current file, surrounding functions, imports, and errors.
"""

import os
import re


class ContextBuilder:
    """Builds context for the AI editor"""
    
    def __init__(self, file_tool):
        self.file_tool = file_tool
    
    def build_context(self, current_file: str, cursor_position: int = None, error: str = None) -> str:
        """
        Build comprehensive context for the editor
        
        Args:
            current_file: Path to the current file
            cursor_position: Current cursor position
            error: Any error message
        
        Returns:
            Context string for the LLM
        """
        context_parts = []
        
        # 1. Current file content
        if os.path.exists(current_file):
            file_content = self.file_tool.read(current_file)
            context_parts.append(f"=== CURRENT FILE: {current_file} ===\n{file_content}")
        
        # 2. Imports
        imports = self.extract_imports(file_content if os.path.exists(current_file) else "")
        if imports:
            context_parts.append(f"=== IMPORTS ===\n{imports}")
        
        # 3. Surrounding functions/classes
        if os.path.exists(current_file):
            surrounding = self.extract_surrounding(file_content, cursor_position or 0)
            if surrounding:
                context_parts.append(f"=== SURROUNDING CODE ===\n{surrounding}")
        
        # 4. Error context
        if error:
            context_parts.append(f"=== ERROR ===\n{error}")
        
        # 5. Project files
        project_files = self.file_tool.list_files()
        if project_files:
            context_parts.append(f"=== PROJECT FILES ===\n" + "\n".join(project_files[:20]))
        
        return "\n\n".join(context_parts)
    
    def extract_imports(self, content: str) -> str:
        """Extract import statements"""
        import re
        
        # Python imports
        python_imports = re.findall(r'^(?:import|from\s+\S+\s+import)\s+.*$', content, re.MULTILINE)
        
        if python_imports:
            return "Python Imports:\n" + "\n".join(python_imports[:15])
        
        return ""
    
    def extract_surrounding(self, content: str, position: int) -> str:
        """Extract code around cursor position"""
        if not content or position < 0:
            return content[:2000] if content else ""
        
        # Get surrounding context (before and after cursor)
        start = max(0, position - 1000)
        end = min(len(content), position + 1000)
        
        surrounding = content[start:end]
        
        # Try to align to function/class boundaries
        lines = surrounding.split('\n')
        
        # Find start of current function/class
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if re.match(r'^(def|class|async def)\s+', line):
                break
            start += len(lines[i]) + 1
        
        return content[start:end]
    
    def get_file_tree(self, directory: str = None) -> str:
        """Get file tree structure"""
        if directory is None:
            directory = self.file_tool.workspace_root
        
        files = self.file_tool.list_files(directory)
        
        tree = []
        for f in files:
            depth = f.count(os.sep)
            prefix = "  " * depth
            tree.append(f"{prefix}├── {os.path.basename(f)}")
        
        return "\n".join(tree)
    
    def get_function_signature(self, content: str, function_name: str) -> str:
        """Get function signature and docstring"""
        pattern = rf'(def|async def)\s+{re.escape(function_name)}\s*\([^)]*\).*?(?=\n(?:def|class|async def|$))'
        match = re.search(pattern, content, re.DOTALL)
        
        return match.group(0) if match else ""


def build_editor_context(file_path: str, error: str = None) -> str:
    """
    Convenience function to build editor context
    
    Args:
        file_path: Path to the current file
        error: Optional error message
    
    Returns:
        Context string
    """
    from core.tools import FileSystemTool
    
    builder = ContextBuilder(FileSystemTool())
    return builder.build_context(file_path, error=error)

