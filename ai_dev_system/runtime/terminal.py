"""
Terminal Tool - Execute terminal commands
=========================================
Provides functions to execute terminal commands.
"""

import subprocess
import os


def execute(command: str, timeout: int = 60, cwd: str = None) -> str:
    """
    Execute a terminal command and return output
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        cwd: Working directory
    
    Returns:
        Combined stdout and stderr
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        
        output = result.stdout + result.stderr
        
        return output if output else f"(No output, return code: {result.returncode})"
        
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error: {str(e)}"


def execute_interactive(command: str, cwd: str = None) -> str:
    """
    Execute an interactive command (returns immediately with start message)
    
    Args:
        command: Command to execute
        cwd: Working directory
    
    Returns:
        Status message
    """
    try:
        # Start the process
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        
        return f"Started process with PID: {process.pid}"
        
    except Exception as e:
        return f"Error: {str(e)}"


def get_system_info() -> dict:
    """Get system information"""
    import platform
    import sys
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": sys.version,
        "architecture": platform.machine(),
        "processor": platform.processor(),
    }


def check_command(command: str) -> bool:
    """Check if a command is available"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                f"where {command}",
                shell=True,
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                f"which {command}",
                shell=True,
                capture_output=True,
                text=True
            )
        
        return result.returncode == 0
        
    except Exception:
        return False

