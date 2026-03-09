"""
Refactor Agent - Improves code quality
=====================================
Refactors code for performance, readability, and best practices.
"""

import json


class RefactorAgent:
    """Agent for refactoring code"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def refactor(self, files: dict) -> dict:
        """
        Refactor the project for better quality
        
        Args:
            files: Dict of filename -> content
        
        Returns:
            dict with filename -> refactored content
        """
        files_str = self._format_files(files)
        
        prompt = f"""
Refactor this project for:

1. Performance - optimize slow operations
2. Readability - clean, understandable code
3. Best practices - follow language idioms
4. Maintainability - easy to modify later
5. Error handling - robust error management

FILES:
{files_str}

Return a JSON object where:
- Keys are file paths that need changes
- Values are the complete refactored file contents

Focus on practical improvements. Keep functionality the same.
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
            
            refactored = json.loads(response)
            
            if not isinstance(refactored, dict):
                return {"error": "Invalid response format"}
            
            return refactored
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {str(e)}", "raw_response": response}
    
    def refactor_file(self, filename: str, content: str, focus: str = None) -> str:
        """
        Refactor a single file
        
        Args:
            filename: Name of the file
            content: Content of the file
            focus: Optional focus area (performance, readability, etc.)
        
        Returns:
            Refactored file content
        """
        focus_str = f"\nFocus on: {focus}" if focus else ""
        
        prompt = f"""
Refactor this file:

FILENAME: {filename}

CODE:
{content}
{focus_str}

Provide the complete refactored code. Maintain the same functionality but improve:
- Code structure
- Naming conventions
- Error handling
- Performance
- Documentation/comments

Return only the code, no explanations.
"""
        
        return self.llm.ask(prompt)
    
    def suggest_improvements(self, files: dict) -> str:
        """
        Suggest areas for improvement
        
        Args:
            files: Project files
        
        Returns:
            Improvement suggestions
        """
        files_str = self._format_files(files)
        
        prompt = f"""
Analyze this code and suggest specific improvements:

FILES:
{files_str}

For each file, list:
1. Code smells or issues
2. Specific refactoring suggestions
3. Performance concerns
4. Security considerations
"""
        
        return self.llm.ask(prompt)
    
    def apply_design_patterns(self, files: dict, pattern: str) -> dict:
        """
        Apply a design pattern to the code
        
        Args:
            files: Project files
            pattern: Design pattern to apply (singleton, factory, observer, etc.)
        
        Returns:
            dict with refactored files
        """
        files_str = self._format_files(files)
        
        prompt = f"""
Apply the {pattern} design pattern to this code:

FILES:
{files_str}

Return a JSON object with the refactored code implementing the {pattern} pattern appropriately.
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
            return {"error": "Failed to parse response"}
    
    def _format_files(self, files: dict) -> str:
        """Format files for prompt"""
        formatted = []
        for filename, content in files.items():
            if filename.startswith("_") or filename in ["error", "raw_response"]:
                continue
            formatted.append(f"\n--- {filename} ---\n{content}")
        return "\n".join(formatted)

