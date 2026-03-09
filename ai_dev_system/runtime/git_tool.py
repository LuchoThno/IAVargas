"""
Git Tool - Git operations
=========================
Provides functions for Git operations.
"""

import subprocess
import os


def git(command: str, cwd: str = None) -> str:
    """
    Execute a git command
    
    Args:
        command: Git command (without 'git' prefix)
        cwd: Working directory
    
    Returns:
        Command output
    """
    full_command = f"git {command}"
    
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode != 0:
            return f"Error: {output}"
        
        return output if output else "Success"
        
    except Exception as e:
        return f"Error: {str(e)}"


def init_repo(path: str = None) -> str:
    """Initialize a git repository"""
    return git("init", cwd=path)


def add(files: str = ".", cwd: str = None) -> str:
    """Stage files"""
    return git(f"add {files}", cwd=cwd)


def commit(message: str, cwd: str = None) -> str:
    """Commit changes"""
    return git(f'commit -m "{message}"', cwd=cwd)


def status(cwd: str = None) -> str:
    """Get git status"""
    return git("status", cwd=cwd)


def log(max_count: int = 10, cwd: str = None) -> str:
    """Get git log"""
    return git(f"log --oneline -n {max_count}", cwd=cwd)


def diff(cwd: str = None) -> str:
    """Get git diff"""
    return git("diff", cwd=cwd)


def branch(cwd: str = None) -> str:
    """Get git branches"""
    return git("branch -a", cwd=cwd)


def checkout(branch: str, create: bool = False, cwd: str = None) -> str:
    """Checkout a branch"""
    if create:
        return git(f"checkout -b {branch}", cwd=cwd)
    return git(f"checkout {branch}", cwd=cwd)


def pull(cwd: str = None) -> str:
    """Pull from remote"""
    return git("pull", cwd=cwd)


def push(cwd: str = None) -> str:
    """Push to remote"""
    return git("push", cwd=cwd)


def clone(url: str, path: str = None) -> str:
    """Clone a repository"""
    if path:
        return git(f"clone {url} {path}")
    return git(f"clone {url}")


def is_repo(path: str = None) -> bool:
    """Check if directory is a git repository"""
    try:
        result = git("rev-parse --git-dir", cwd=path)
        return "Error" not in result
    except Exception:
        return False


def get_current_branch(cwd: str = None) -> str:
    """Get current branch name"""
    result = git("rev-parse --abbrev-ref HEAD", cwd=cwd)
    return result.strip()

