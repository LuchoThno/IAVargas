"""
Planner Agent - Creates software architecture plans
====================================================
Analyzes tasks and creates detailed project architecture plans.
"""

import json


class PlannerAgent:
    """Agent for creating project architecture plans"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def plan(self, task: str) -> dict:
        """
        Create an architecture plan for the given task
        
        Args:
            task: The task description
        
        Returns:
            dict with language, framework, files, run_command, dependencies
        """
        prompt = f"""
You are a senior software architect.

Task:
{task}

Create a detailed project architecture plan. Return a JSON object with:
- language: Programming language (e.g., "python", "javascript", "go")
- framework: Framework to use (e.g., "fastapi", "react", "flask")
- files: List of files to create with their purpose
- run_command: Command to run the project
- dependencies: List of dependencies needed

Be specific and practical. Consider best practices for the chosen stack.
"""
        
        response = self.llm.ask(prompt)
        
        # Try to parse JSON
        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError:
            # Return a structured response even if not valid JSON
            return {
                "language": "python",
                "framework": "unknown",
                "files": [{"name": "main.py", "purpose": "Main entry point"}],
                "run_command": "python main.py",
                "dependencies": [],
                "raw_response": response
            }
    
    def suggest_improvements(self, current_plan: dict, feedback: str) -> dict:
        """
        Suggest improvements to an existing plan
        
        Args:
            current_plan: Current architecture plan
            feedback: User feedback or issues
        
        Returns:
            Updated plan
        """
        prompt = f"""
Current architecture plan:
{json.dumps(current_plan, indent=2)}

User feedback or issues:
{feedback}

Suggest improvements to address the feedback. Return an improved JSON plan.
"""
        
        response = self.llm.ask(prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError:
            return current_plan

