"""
Runner - Execute commands and programs
======================================
Provides functions to run commands and capture output.
"""

import subprocess
import os
import json


class Runner:
    """Execute commands and programs"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir or "ai_dev_system/workspace/projects"
        os.makedirs(self.working_dir, exist_ok=True)
    
    def run(self, command: str, timeout: int = 60, shell: bool = True) -> dict:
        """
        Run a command and return the result
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            shell: Whether to use shell
        
        Returns:
            dict with success, stdout, stderr, returncode
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_dir
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def run_python(self, code: str, timeout: int = 30) -> dict:
        """Run Python code"""
        # Write code to a temp file and execute
        import tempfile
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                f'python "{temp_file}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_dir
            )
            
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def run_tests(self, test_framework: str = "pytest", path: str = None) -> dict:
        """Run tests"""
        if path is None:
            path = self.working_dir
        
        if test_framework == "pytest":
            command = f'pytest "{path}" -v'
        elif test_framework == "unittest":
            command = f'python -m unittest discover -s "{path}"'
        else:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Unknown test framework: {test_framework}",
                "returncode": -1
            }
        
        return self.run(command, timeout=120)
    
    def install_requirements(self, requirements_file: str = None) -> dict:
        """Install Python requirements"""
        if requirements_file is None:
            requirements_file = os.path.join(self.working_dir, "requirements.txt")
        
        if not os.path.exists(requirements_file):
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Requirements file not found: {requirements_file}",
                "returncode": -1
            }
        
        return self.run(f'pip install -r "{requirements_file}"', timeout=300)


# Default runner instance
runner = Runner()

