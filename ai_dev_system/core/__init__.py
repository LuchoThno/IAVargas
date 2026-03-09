"""
AI Dev System - Core Module
============================
Core components for the AI Developer System.
"""

from .llm import LLMClient, get_default_client
from .memory import Memory, memory, save_to_memory, search_memory, get_memory_by_category, clear_memory
from .tools import FileSystemTool, fs
from .patcher import apply_patch, apply_patches, find_and_replace, insert_after, insert_before

__all__ = [
    'LLMClient',
    'get_default_client',
    'Memory',
    'memory',
    'save_to_memory',
    'search_memory',
    'get_memory_by_category',
    'clear_memory',
    'FileSystemTool',
    'fs',
    'apply_patch',
    'apply_patches',
    'find_and_replace',
    'insert_after',
    'insert_before',
]

