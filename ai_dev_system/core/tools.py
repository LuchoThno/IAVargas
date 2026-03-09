"""
Tool System - Provides tool interface for agents
=================================================
File system operations for reading, writing, and listing files.
"""

import os
import shutil
import json


class FileSystemTool:
    """File system operations tool for the AI Dev System"""
    
    def __init__(self, workspace_root: str = "ai_dev_system/workspace/projects"):
        self.workspace_root = workspace_root
        os.makedirs(workspace_root, exist_ok=True)
    
    def read(self, path: str) -> str:
        """Read file content"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write(self, path: str, content: str):
        """Write content to file"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Success: Written to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def list_files(self, directory: str = None) -> list:
        """List all files in directory recursively"""
        if directory is None:
            directory = self.workspace_root
        
        result = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for f in files:
                    if not f.startswith('.'):
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, self.workspace_root)
                        result.append(rel_path)
        except Exception as e:
            return [f"Error: {str(e)}"]
        
        return result
    
    def exists(self, path: str) -> bool:
        """Check if file or directory exists"""
        return os.path.exists(path)
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        return os.path.isfile(path)
    
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory"""
        return os.path.isdir(path)
    
    def delete(self, path: str) -> bool:
        """Delete file or directory"""
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"Error deleting: {e}")
            return False
    
    def create_directory(self, path: str):
        """Create directory"""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Success: Created {path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"
    
    def get_file_info(self, path: str) -> dict:
        """Get file information"""
        if not os.path.exists(path):
            return {"error": "File not found"}
        
        stat = os.stat(path)
        return {
            "path": path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": os.path.isfile(path),
            "is_dir": os.path.isdir(path)
        }
    
    def read_json(self, path: str) -> dict:
        """Read JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def write_json(self, path: str, data: dict):
        """Write JSON file"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return f"Success: Written JSON to {path}"
        except Exception as e:
            return f"Error writing JSON: {str(e)}"


# Default file system tool instance
fs = FileSystemTool()

