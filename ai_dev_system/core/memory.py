"""
Memory System - Stores solved bugs, architecture decisions, code snippets, documentation
==============================================================================
Simple JSON-based memory storage for the AI Dev System.
"""

import json
import os
from datetime import datetime


class Memory:
    """Simple memory storage for the AI Dev System"""
    
    def __init__(self, memory_path: str = "ai_dev_system/memory/log.json"):
        self.memory_path = memory_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the memory file exists"""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, 'w') as f:
                json.dump([], f)
    
    def save(self, item: dict):
        """Save an item to memory"""
        data = self.load()
        
        # Add timestamp if not present
        if "timestamp" not in item:
            item["timestamp"] = datetime.now().isoformat()
        
        data.append(item)
        
        with open(self.memory_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> list:
        """Load all memory items"""
        if not os.path.exists(self.memory_path):
            return []
        
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def search(self, query: str) -> list:
        """Search memory for items containing the query"""
        data = self.load()
        results = []
        
        for item in data:
            # Search in all string values
            item_str = json.dumps(item).lower()
            if query.lower() in item_str:
                results.append(item)
        
        return results
    
    def get_by_category(self, category: str) -> list:
        """Get items by category"""
        data = self.load()
        return [item for item in data if item.get("category") == category]
    
    def clear(self):
        """Clear all memory"""
        with open(self.memory_path, 'w') as f:
            json.dump([], f)
    
    def get_recent(self, limit: int = 10) -> list:
        """Get recent memory items"""
        data = self.load()
        return data[-limit:] if len(data) > limit else data


# Default memory instance
memory = Memory()


# Convenience functions
def save_to_memory(item: dict):
    """Save an item to memory"""
    memory.save(item)


def search_memory(query: str) -> list:
    """Search memory"""
    return memory.search(query)


def get_memory_by_category(category: str) -> list:
    """Get memory by category"""
    return memory.get_by_category(category)


def clear_memory():
    """Clear all memory"""
    memory.clear()

