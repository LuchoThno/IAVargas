"""
Patch System - Safe code editing
================================
Provides functions to safely apply patches to existing files.
"""

import os
import re


def apply_patch(file_path: str, old_code: str, new_code: str) -> str:
    """
    Apply a patch to a file by replacing old_code with new_code
    
    Args:
        file_path: Path to the file to patch
        old_code: The code to replace
        new_code: The new code to insert
    
    Returns:
        Success or error message
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if old_code exists
        if old_code not in content:
            return f"Error: Could not find the specified code in {file_path}"
        
        # Apply the patch
        new_content = content.replace(old_code, new_code)
        
        # Write the patched file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Success: Patched {file_path}"
    
    except Exception as e:
        return f"Error applying patch: {str(e)}"


def apply_patches(file_path: str, patches: list) -> str:
    """
    Apply multiple patches to a file
    
    Args:
        file_path: Path to the file to patch
        patches: List of dicts with 'old' and 'new' keys
    
    Returns:
        Success or error message
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply each patch
        for patch in patches:
            old_code = patch.get('old', '')
            new_code = patch.get('new', '')
            
            if old_code not in content:
                return f"Error: Could not find code to patch: {old_code[:50]}..."
            
            content = content.replace(old_code, new_code)
        
        # Write the patched file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Success: Applied {len(patches)} patches to {file_path}"
    
    except Exception as e:
        return f"Error applying patches: {str(e)}"


def find_and_replace(file_path: str, search_pattern: str, replacement: str, use_regex: bool = False) -> str:
    """
    Find and replace text in a file
    
    Args:
        file_path: Path to the file
        search_pattern: Pattern to search for
        replacement: Replacement text
        use_regex: Whether to use regex for matching
    
    Returns:
        Success or error message
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Perform replacement
        if use_regex:
            new_content, count = re.subn(search_pattern, replacement, content)
            if count == 0:
                return f"Warning: No matches found for pattern: {search_pattern}"
        else:
            if search_pattern not in content:
                return f"Warning: No matches found for: {search_pattern}"
            new_content = content.replace(search_pattern, replacement)
        
        # Write the patched file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Success: Replaced text in {file_path}"
    
    except Exception as e:
        return f"Error: {str(e)}"


def insert_after(file_path: str, after_pattern: str, new_code: str) -> str:
    """
    Insert new code after a specific pattern
    
    Args:
        file_path: Path to the file
        after_pattern: Pattern to insert after
        new_code: Code to insert
    
    Returns:
        Success or error message
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if pattern exists
        if after_pattern not in content:
            return f"Error: Pattern not found: {after_pattern}"
        
        # Find the position after the pattern
        pos = content.find(after_pattern) + len(after_pattern)
        
        # Insert the new code
        new_content = content[:pos] + new_code + content[pos:]
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Success: Inserted code after pattern in {file_path}"
    
    except Exception as e:
        return f"Error: {str(e)}"


def insert_before(file_path: str, before_pattern: str, new_code: str) -> str:
    """
    Insert new code before a specific pattern
    
    Args:
        file_path: Path to the file
        before_pattern: Pattern to insert before
        new_code: Code to insert
    
    Returns:
        Success or error message
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if pattern exists
        if before_pattern not in content:
            return f"Error: Pattern not found: {before_pattern}"
        
        # Find the position before the pattern
        pos = content.find(before_pattern)
        
        # Insert the new code
        new_content = content[:pos] + new_code + content[pos:]
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Success: Inserted code before pattern in {file_path}"
    
    except Exception as e:
        return f"Error: {str(e)}"

