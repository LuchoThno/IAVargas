"""
AI Dev System
=============
A Devin-like Autonomous Developer + Cursor-style AI Editor (Local)

This system can:
- Design software architecture
- Generate full codebases
- Edit files intelligently
- Execute programs
- Debug runtime errors
- Write and run tests
- Refactor code
- Perform research
- Use terminal tools
- Commit changes to git
- Iterate until software works

Usage:
    from ai_dev_system import create_orchestrator
    
    orchestrator = create_orchestrator()
    result = orchestrator.execute("create a fastapi user API")
"""

from .core import (
    LLMClient,
    get_default_client,
    Memory,
    FileSystemTool,
    fs,
    apply_patch,
    apply_patches,
)

from .agents import (
    Orchestrator,
    create_orchestrator,
    PlannerAgent,
    ResearchAgent,
    CoderAgent,
    DebuggerAgent,
    TestAgent,
    RefactorAgent,
)

from .editor import (
    explain,
    refactor,
    add_tests,
    fix,
    improve,
    complete,
    execute_command,
)

from .runtime import (
    Runner,
    runner,
    execute,
    git,
    init_repo,
)

__version__ = "1.0.0"

__all__ = [
    # Core
    'LLMClient',
    'get_default_client',
    'Memory',
    'FileSystemTool',
    'fs',
    'apply_patch',
    'apply_patches',
    
    # Agents
    'Orchestrator',
    'create_orchestrator',
    'PlannerAgent',
    'ResearchAgent',
    'CoderAgent',
    'DebuggerAgent',
    'TestAgent',
    'RefactorAgent',
    
    # Editor
    'explain',
    'refactor',
    'add_tests',
    'fix',
    'improve',
    'complete',
    'execute_command',
    
    # Runtime
    'Runner',
    'runner',
    'execute',
    'git',
    'init_repo',
]

