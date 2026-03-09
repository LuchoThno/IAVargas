"""
AI Commands - Cursor-like editor commands
========================================
Commands for the AI-powered code editor.
"""

from .context_builder import ContextBuilder
from core.tools import FileSystemTool
from core.llm import LLMClient


def explain(code: str, llm: LLMClient = None) -> str:
    """
    Explain the selected code or concept in simple terms
    
    Args:
        code: Code to explain
        llm: LLM client (optional)
    
    Returns:
        Explanation
    """
    if llm is None:
        llm = LLMClient()
    
    prompt = f"""
Explain this code in simple terms:

```
{code}
```

Provide:
1. What the code does (summary)
2. How it works (step by step)
3. Key concepts or patterns used

Use simple language suitable for someone learning to code.
"""
    
    return llm.ask(prompt)


def refactor(code: str, llm: LLMClient = None, focus: str = None) -> str:
    """
    Suggest improvements for code quality and maintainability
    
    Args:
        code: Code to refactor
        llm: LLM client (optional)
        focus: Optional focus area (readability, performance, etc.)
    
    Returns:
        Refactored code
    """
    if llm is None:
        llm = LLMClient()
    
    focus_str = f"\nFocus on: {focus}" if focus else ""
    
    prompt = f"""
Refactor this code for better quality:{focus_str}

Original code:
```
{code}
```

Provide the refactored code with:
- Better naming
- Improved structure
- Clearer comments
- Error handling if missing
- Best practices

Return only the refactored code, no explanations.
"""
    
    return llm.ask(prompt)


def add_tests(code: str, llm: LLMClient = None) -> str:
    """
    Add tests for the selected code
    
    Args:
        code: Code to test
        llm: LLM client (optional)
    
    Returns:
        Test code
    """
    if llm is None:
        llm = LLMClient()
    
    prompt = f"""
Generate pytest-style unit tests for this code:

```
{code}
```

Include:
- Test class
- Test methods for each function/method
- Proper assertions
- Edge case tests

Return only the test code.
"""
    
    return llm.ask(prompt)


def fix(code: str, error: str, llm: LLMClient = None) -> str:
    """
    Fix errors in the code
    
    Args:
        code: Code with errors
        error: Error message
        llm: LLM client (optional)
    
    Returns:
        Fixed code
    """
    if llm is None:
        llm = LLMClient()
    
    prompt = f"""
Fix this code that has an error:

ERROR:
{error}

CODE:
```
{code}
```

Provide the corrected code. Return only the fixed code, no explanations.
"""
    
    return llm.ask(prompt)


def improve(code: str, llm: LLMClient = None) -> str:
    """
    Suggest improvements for code
    
    Args:
        code: Code to improve
        llm: LLM client (optional)
    
    Returns:
        Improvement suggestions
    """
    if llm is None:
        llm = LLMClient()
    
    prompt = f"""
Analyze this code and suggest improvements:

```
{code}
```

Provide specific, actionable suggestions for:
1. Performance
2. Readability
3. Maintainability
4. Security
5. Best practices
"""
    
    return llm.ask(prompt)


def complete(code: str, llm: LLMClient = None) -> str:
    """
    Complete the partial code
    
    Args:
        code: Partial code
        llm: LLM client (optional)
    
    Returns:
        Completed code
    """
    if llm is None:
        llm = LLMClient()
    
    prompt = f"""
Complete this partial code:

```
{code}
```

Provide the complete, functional code. Return only the completed code.
"""
    
    return llm.ask(prompt)


def generate_docstring(code: str, llm: LLMClient = None) -> str:
    """
    Generate docstrings for functions/classes
    
    Args:
        code: Code to document
        llm: LLM client (optional)
    
    Returns:
        Code with docstrings
    """
    if llm is None:
        llm = LLMClient()
    
    prompt = f"""
Add comprehensive docstrings to this code:

```
{code}
```

Use Google-style docstrings with:
- Description
- Args
- Returns
- Raises (if applicable)

Return the code with docstrings added.
"""
    
    return llm.ask(prompt)


def chat_with_code(code: str, question: str, llm: LLMClient = None) -> str:
    """
    Ask questions about the code
    
    Args:
        code: Code to analyze
        question: Question about the code
        llm: LLM client (optional)
    
    Returns:
        Answer
    """
    if llm is None:
        llm = LLMClient()
    
    prompt = f"""
Given this code:

```
{code}
```

Question: {question}

Answer the question about this code.
"""
    
    return llm.ask(prompt)


# Command registry
COMMANDS = {
    "explain": explain,
    "refactor": refactor,
    "add-tests": add_tests,
    "fix": fix,
    "improve": improve,
    "complete": complete,
    "generate-docstring": generate_docstring,
    "chat": chat_with_code,
}


def execute_command(command: str, code: str, llm: LLMClient = None, **kwargs) -> str:
    """
    Execute an editor command
    
    Args:
        command: Command name
        code: Code context
        llm: LLM client
        **kwargs: Additional arguments
    
    Returns:
        Command result
    """
    if command not in COMMANDS:
        return f"Unknown command: {command}"
    
    return COMMANDS[command](code, llm, **kwargs)

