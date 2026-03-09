"""
Debugger Agent - Fixes runtime errors
=====================================
Analyzes errors and provides fixes.
"""

import json


class DebuggerAgent:
    """Agent for debugging and fixing errors"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def fix(self, error: str, files: dict) -> dict:
        """
        Analyze error and provide fixes
        
        Args:
            error: Error message
            files: Dict of filename -> content for relevant files
        
        Returns:
            dict with filename -> new_content patches
        """
        files_str = self._format_files(files)
        
        prompt = f"""
The project failed with this error:

ERROR:
{error}

FILES:
{files_str}

Analyze the error and provide corrected code. Return a JSON object where:
- Keys are file paths that need to be modified
- Values are the complete corrected file contents

Fix all issues to make the project work. Provide the FULL corrected files, not just snippets.
"""
        
        response = self.llm.ask(prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                try:
                    response = response.split("```")[1].split("```")[0]
                except:
                    pass
            
            patches = json.loads(response)
            
            if not isinstance(patches, dict):
                return {"error": "Invalid response format"}
            
            return patches
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {str(e)}", "raw_response": response}
    
    def analyze_error(self, error: str) -> str:
        """
        Analyze an error and explain it
        
        Args:
            error: Error message
        
        Returns:
            Analysis explanation
        """
        prompt = f"""
Analyze this error and explain what's wrong:

ERROR:
{error}

Provide a clear explanation of:
1. What the error means
2. What likely caused it
3. How to fix it
"""
        
        return self.llm.ask(prompt)
    
    def suggest_fixes(self, error: str, file_content: str) -> list:
        """
        Suggest multiple fix options
        
        Args:
            error: Error message
            file_content: Content of the file with the error
        
        Returns:
            List of potential fixes
        """
        prompt = f"""
Error in this code:

ERROR:
{error}

CODE:
{file_content}

Suggest 2-3 possible fixes. Return JSON:
[
    {{"description": "fix description", "code": "fixed code snippet"}}
]
"""
        
        response = self.llm.ask(prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                try:
                    response = response.split("```")[1].split("```")[0]
                except:
                    pass
            
            return json.loads(response)
        except json.JSONDecodeError:
            return []
    
    def _format_files(self, files: dict) -> str:
        """Format files for prompt"""
        formatted = []
        for filename, content in files.items():
            if filename.startswith("_") or filename in ["error", "raw_response"]:
                continue
            formatted.append(f"\n--- {filename} ---\n{content}")
        return "\n".join(formatted)

