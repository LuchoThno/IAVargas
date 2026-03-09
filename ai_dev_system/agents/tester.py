"""
Test Generator Agent - Generates tests for projects
====================================================
Generates test files for projects.
"""

import json


class TestAgent:
    """Agent for generating tests"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate_tests(self, files: dict) -> dict:
        """
        Generate tests for the project
        
        Args:
            files: Dict of filename -> content for the project
        
        Returns:
            dict with test filename -> test content
        """
        files_str = self._format_files(files)
        
        prompt = f"""
Generate comprehensive tests for this project.

PROJECT FILES:
{files_str}

Generate test files using pytest or unittest. Return a JSON object where:
- Keys are test file paths (e.g., "tests/test_main.py", "test_app.py")
- Values are the complete test file contents

Include:
- Unit tests for main functions/classes
- Integration tests if applicable
- Edge case tests
- Proper assertions

Make tests complete and runnable.
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
            
            tests = json.loads(response)
            
            if not isinstance(tests, dict):
                return {"error": "Invalid response format"}
            
            return tests
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {str(e)}", "raw_response": response}
    
    def generate_unit_test(self, filename: str, content: str) -> str:
        """
        Generate unit tests for a single file
        
        Args:
            filename: Name of the file to test
            content: Content of the file
        
        Returns:
            Test file content
        """
        prompt = f"""
Generate unit tests for this file:

FILENAME: {filename}

CODE:
{content}

Generate complete pytest-style unit tests. Include:
- Test class if applicable
- Test methods for each function/method
- Proper setup/teardown if needed
- Descriptive test names
- Assertions for expected behavior
"""
        
        return self.llm.ask(prompt)
    
    def suggest_test_coverage(self, files: dict) -> str:
        """
        Suggest areas that need test coverage
        
        Args:
            files: Project files
        
        Returns:
            Suggestions for test coverage
        """
        files_str = self._format_files(files)
        
        prompt = f"""
Analyze this project and suggest test coverage areas:

FILES:
{files_str}

List:
1. Critical functions/classes that need testing
2. Edge cases to consider
3. Integration points that need tests
4. Any missing test scenarios
"""
        
        return self.llm.ask(prompt)
    
    def _format_files(self, files: dict) -> str:
        """Format files for prompt"""
        formatted = []
        for filename, content in files.items():
            if filename.startswith("_") or filename in ["error", "raw_response"]:
                continue
            formatted.append(f"\n--- {filename} ---\n{content}")
        return "\n".join(formatted)

