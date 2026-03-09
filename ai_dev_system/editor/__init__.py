"""
AI Dev System - Editor Module
==============================
Cursor-like AI editor commands.
"""

from .context_builder import ContextBuilder, build_editor_context
from .ai_commands import (
    explain,
    refactor,
    add_tests,
    fix,
    improve,
    complete,
    generate_docstring,
    chat_with_code,
    execute_command,
    COMMANDS
)

__all__ = [
    'ContextBuilder',
    'build_editor_context',
    'explain',
    'refactor',
    'add_tests',
    'fix',
    'improve',
    'complete',
    'generate_docstring',
    'chat_with_code',
    'execute_command',
    'COMMANDS',
]

