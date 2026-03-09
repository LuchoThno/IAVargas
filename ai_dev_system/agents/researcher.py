"""
Research Agent - Research documentation and best practices
==========================================================
Researches documentation and best practices before coding.
"""

import json


class ResearchAgent:
    """Agent for researching documentation and best practices"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def research(self, task: str) -> str:
        """
        Research the best approach to implement a task
        
        Args:
            task: The task to research
        
        Returns:
            Concise technical notes
        """
        prompt = f"""
Research the best approach to implement:

{task}

Provide concise technical notes including:
1. Recommended libraries/frameworks
2. Best practices for this type of project
3. Common pitfalls to avoid
4. Architecture recommendations
5. Any relevant design patterns

Keep it practical and actionable.
"""
        
        return self.llm.ask(prompt)
    
    def research_libraries(self, language: str, requirements: list) -> dict:
        """
        Research suitable libraries for requirements
        
        Args:
            language: Programming language
            requirements: List of requirements
        
        Returns:
            dict with recommended libraries
        """
        req_str = ", ".join(requirements)
        
        prompt = f"""
For a {language} project with requirements: {req_str}

Recommend the best libraries/frameworks. Return JSON:
{{
    "libraries": [
        {{"name": "libname", "purpose": "what it does", " alternatives": ["alt1", "alt2"]}}
    ],
    "reasons": "why these choices"
}}
"""
        
        response = self.llm.ask(prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError:
            return {"libraries": [], "raw_response": response}
    
    def get_best_practices(self, framework: str) -> str:
        """
        Get best practices for a framework
        
        Args:
            framework: Framework name
        
        Returns:
            Best practices guide
        """
        prompt = f"""
What are the best practices for developing applications with {framework}?

Include:
1. Project structure
2. Configuration management
3. Error handling
4. Testing strategies
5. Deployment recommendations
"""
        
        return self.llm.ask(prompt)
    
    def compare_options(self, options: list, criteria: list) -> dict:
        """
        Compare multiple options based on criteria
        
        Args:
            options: List of options to compare
            criteria: List of criteria
        
        Returns:
            Comparison results
        """
        options_str = "\n".join([f"- {opt}" for opt in options])
        criteria_str = "\n".join([f"- {c}" for c in criteria])
        
        prompt = f"""
Compare these options:
{options_str}

Based on these criteria:
{criteria_str}

Provide a detailed comparison and recommendation. Return JSON:
{{
    "recommendation": "best option",
    "analysis": {{"option": {{"pros": [], "cons": [], "score": 0}}}}
}}
"""
        
        response = self.llm.ask(prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}

