"""
Code Generator Agent - Generates full codebases
================================================
Generates complete code based on tasks, plans, and research.
"""

import json
import os


class CoderAgent:
    """Agent for generating code"""
    
    def __init__(self, llm, file_tool):
        self.llm = llm
        self.file_tool = file_tool
    
    def generate(self, task: str, plan: dict, research: str = None) -> dict:
        """
        Generate a full project based on task, plan, and research
        
        Args:
            task: The task description
            plan: Architecture plan
            research: Research notes
        
        Returns:
            dict with filename -> code mappings
        """
        plan_str = json.dumps(plan, indent=2)
        
        prompt = f"""
Generate a complete project.

TASK:
{task}

ARCHITECTURE PLAN:
{plan_str}

RESEARCH:
{research or "No research provided"}

Generate all necessary files for this project. Return a JSON object where:
- Keys are file paths (e.g., "main.py", "requirements.txt", "src/utils.py")
- Values are the complete file contents

Include all files necessary for a working project:
- Main entry point
- Requirements/dependencies
- Configuration files
- Source files
- Test files if applicable

The code should be complete, functional, and follow best practices.
"""
        
        response = self.llm.ask(prompt)
        
        # Parse the response to get file mappings
        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                # Try to find JSON in the response
                try:
                    response = response.split("```")[1].split("```")[0]
                except:
                    pass
            
            files = json.loads(response)
            
            # Validate it's a dict
            if not isinstance(files, dict):
                return {"error": "Invalid response format", "raw": response}
            
            return files
            
        except json.JSONDecodeError as e:
            # Return error info
            return {"error": f"JSON parse error: {str(e)}", "raw_response": response}
    
    def generate_file(self, filename: str, context: dict) -> str:
        """
        Generate a single file based on context
        
        Args:
            filename: Name of the file to generate
            context: Context for generation
        
        Returns:
            File content
        """
        prompt = f"""
Generate the file: {filename}

Context:
{json.dumps(context, indent=2)}

Provide the complete file content. No explanations, just the code.
"""
        
        return self.llm.ask(prompt)
    
    def save_project(self, files: dict, base_path: str = "ai_dev_system/workspace/projects") -> dict:
        """
        Save generated files to disk
        
        Args:
            files: Dict of filename -> content
            base_path: Base directory for saving
        
        Returns:
            dict with success status and any errors
        """
        results = {"saved": [], "errors": []}
        
        for filename, content in files.items():
            # Skip non-file entries
            if filename.startswith("_") or filename in ["error", "raw_response"]:
                continue
            
            filepath = os.path.join(base_path, filename)
            
            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                results["saved"].append(filename)
            except Exception as e:
                results["errors"].append(f"{filename}: {str(e)}")
        
        return results
    
    def update_file(self, filename: str, old_code: str, new_code: str, base_path: str = "ai_dev_system/workspace/projects") -> str:
        """
        Update a specific file with new code
        
        Args:
            filename: File to update
            old_code: Code to replace
            new_code: New code
            base_path: Base directory
        
        Returns:
            Success or error message
        """
        from core.patcher import apply_patch
        
        filepath = os.path.join(base_path, filename)
        return apply_patch(filepath, old_code, new_code)

