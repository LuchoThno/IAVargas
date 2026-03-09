# Plan Mejora Local AIVargas Dev System

## Devin-like Autonomous Developer + Cursor-style AI Editor (Local)

Author: AI System Design
Target Runtime: Local Machine
LLM Runtime: Ollama

---

# 1. Overview

This project defines a **local AI software engineering system** combining:

• Autonomous developer similar to Devin
• Interactive coding editor similar to Cursor
• Local LLM runtime via Ollama

The system can:

• Design software architecture
• Generate full codebases
• Edit files intelligently
• Execute programs
• Debug runtime errors
• Write and run tests
• Refactor code
• Perform research
• Use terminal tools
• Commit changes to git
• Iterate until software works

This creates a **local AI software engineer** capable of autonomously building projects.

---

# 2. System Architecture

```
USER
 │
 ▼
AI Interface (CLI / Web / Editor)
 │
 ▼
Agent Orchestrator
 │
 ├── Planner Agent
 ├── Research Agent
 ├── Code Generator Agent
 ├── Refactor Agent
 ├── Test Generator Agent
 ├── Debugger Agent
 │
 ▼
Tool System
 │
 ├── File System
 ├── Terminal
 ├── Git
 ├── Runner
 └── Browser
 │
 ▼
Memory System
 │
 ├── Vector DB
 └── Logs
```

Execution Loop:

```
Task
 ↓
Research
 ↓
Architecture Plan
 ↓
Generate Code
 ↓
Run Project
 ↓
Tests
 ↓
Debug
 ↓
Refactor
 ↓
Repeat until working
```

---

# 3. Project Structure

```
ai_dev_system/

app.py

core/
    llm.py
    memory.py
    tools.py
    patcher.py

agents/
    orchestrator.py
    planner.py
    coder.py
    debugger.py
    tester.py
    researcher.py
    refactor.py

editor/
    context_builder.py
    ai_commands.py

runtime/
    terminal.py
    git_tool.py
    runner.py

workspace/
    projects/

memory/
    vector_store/

logs/
```

---

# 4. Installation

Install Python dependencies:

```
pip install ollama
pip install pydantic
pip install rich
pip install sentence-transformers
pip install faiss-cpu
```

Install LLM models:

```
ollama pull llama3
ollama pull deepseek-coder
ollama pull qwen2.5-coder
```

Recommended hardware:

```
RAM: 32GB+
GPU: optional
Disk: 20GB
```

---

# 5. LLM Client

File:

```
core/llm.py
```

```python
import ollama

class LLMClient:

    def __init__(self, model="deepseek-coder"):
        self.model = model

    def ask(self, prompt):

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response["message"]["content"]
```

---

# 6. Memory System

File:

```
core/memory.py
```

Stores:

• solved bugs
• architecture decisions
• code snippets
• documentation

```python
import json
import os

class Memory:

    def __init__(self):
        self.path = "memory/log.json"

    def save(self, item):

        if not os.path.exists(self.path):
            data = []
        else:
            data = json.load(open(self.path))

        data.append(item)

        json.dump(data, open(self.path,"w"), indent=2)

    def load(self):

        if not os.path.exists(self.path):
            return []

        return json.load(open(self.path))
```

---

# 7. Tool System

File:

```
core/tools.py
```

Provides tool interface for agents.

```python
import os

class FileSystemTool:

    def read(self, path):
        return open(path).read()

    def write(self, path, content):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path,"w") as f:
            f.write(content)

    def list_files(self, directory):

        result = []

        for root,dirs,files in os.walk(directory):
            for f in files:
                result.append(os.path.join(root,f))

        return result
```

---

# 8. Planner Agent

File:

```
agents/planner.py
```

Purpose:

Create architecture plan.

```python
class PlannerAgent:

    def __init__(self, llm):
        self.llm = llm

    def plan(self, task):

        prompt = f"""
You are a senior software architect.

Task:
{task}

Create a project architecture.

Return JSON:

language
framework
files
run_command
dependencies
"""

        return self.llm.ask(prompt)
```

---

# 9. Research Agent

File:

```
agents/researcher.py
```

Purpose:

Research documentation before coding.

```python
class ResearchAgent:

    def __init__(self,llm):
        self.llm = llm

    def research(self,task):

        prompt = f"""
Research the best approach to implement:

{task}

Return concise technical notes.
"""

        return self.llm.ask(prompt)
```

---

# 10. Code Generator Agent

File:

```
agents/coder.py
```

```python
class CoderAgent:

    def __init__(self,llm):
        self.llm = llm

    def generate(self,task,plan,research):

        prompt = f"""
Generate a full project.

TASK:
{task}

PLAN:
{plan}

RESEARCH:
{research}

Return JSON:

filename
code
"""

        return self.llm.ask(prompt)
```

---

# 11. Test Generator

File:

```
agents/tester.py
```

```python
class TestAgent:

    def __init__(self,llm):
        self.llm = llm

    def generate_tests(self,files):

        prompt = f"""
Generate tests for this project.

FILES:
{files}

Return JSON test files.
"""

        return self.llm.ask(prompt)
```

---

# 12. Debugger Agent

File:

```
agents/debugger.py
```

```python
class DebuggerAgent:

    def __init__(self,llm):
        self.llm = llm

    def fix(self,error,files):

        prompt=f"""
Project failed.

ERROR:
{error}

FILES:
{files}

Return corrected patches.
"""

        return self.llm.ask(prompt)
```

---

# 13. Refactor Agent

File:

```
agents/refactor.py
```

Improves code quality.

```python
class RefactorAgent:

    def __init__(self,llm):
        self.llm=llm

    def refactor(self,files):

        prompt=f"""
Refactor the project for:

performance
readability
best practices

FILES:
{files}

Return improved patches.
"""

        return self.llm.ask(prompt)
```

---

# 14. Runner

File:

```
runtime/runner.py
```

```python
import subprocess

class Runner:

    def run(self,command):

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        return {
            "success": result.returncode==0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
```

---

# 15. Terminal Tool

File:

```
runtime/terminal.py
```

```python
import subprocess

def execute(cmd):

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr
```

---

# 16. Git Tool

File:

```
runtime/git_tool.py
```

```python
import subprocess

def git(cmd):

    result = subprocess.run(
        f"git {cmd}",
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout
```

---

# 17. Patch System

File:

```
core/patcher.py
```

Ensures safe edits.

```python
def apply_patch(file,patch):

    text=open(file).read()

    text=text.replace(
        patch["old"],
        patch["new"]
    )

    open(file,"w").write(text)
```

---

# 18. Orchestrator

File:

```
agents/orchestrator.py
```

Main decision engine.

```python
class Orchestrator:

    def __init__(self,llm):

        from agents.planner import PlannerAgent
        from agents.coder import CoderAgent
        from agents.debugger import DebuggerAgent
        from agents.tester import TestAgent
        from agents.researcher import ResearchAgent

        self.planner=PlannerAgent(llm)
        self.coder=CoderAgent(llm)
        self.debugger=DebuggerAgent(llm)
        self.tester=TestAgent(llm)
        self.researcher=ResearchAgent(llm)

    def execute(self,task):

        research=self.researcher.research(task)

        plan=self.planner.plan(task)

        files=self.coder.generate(task,plan,research)

        tests=self.tester.generate_tests(files)

        project=dict(files,**tests)

        for i in range(10):

            result=self.run_project()

            if result["success"]:
                return "SUCCESS"

            fixes=self.debugger.fix(result["stderr"],project)

            project.update(fixes)

        return "FAILED"
```

---

# 19. Editor Commands (Cursor-like)

File:

```
editor/ai_commands.py
```

Commands supported:

```
/explain
/refactor
/add-tests
/fix
/improve
```

Example:

```python
def explain(code,llm):

    prompt=f"""
Explain this code:

{code}
"""

    return llm.ask(prompt)
```

---

# 20. Context Builder

File:

```
editor/context_builder.py
```

Provides relevant context to LLM.

Includes:

• current file
• surrounding functions
• imports
• errors

---

# 21. Main Entry

File:

```
app.py
```

```python
from core.llm import LLMClient
from agents.orchestrator import Orchestrator

def main():

    task=input("Task: ")

    llm=LLMClient()

    orch=Orchestrator(llm)

    result=orch.execute(task)

    print(result)

if __name__=="__main__":
    main()
```

---

# 22. Example Usage

User input:

```
create a fastapi user API with authentication
```

Execution:

```
research documentation
create architecture
generate code
generate tests
run project
debug
refactor
```

Final result:

Working project generated locally.

---

# 23. Future Improvements

Add:

### Web Interface

React dashboard.

### Browser Tool

Automatic documentation search.

### Multi-agent planning

Hierarchical agents.

### Docker sandbox

Run projects safely.

### Continuous learning

Store solved bugs.

---

# 24. Expected Capabilities

The system becomes a **local AI developer** capable of:

• generating complete applications
• debugging runtime errors
• writing tests
• refactoring code
• researching documentation
• managing git repositories
• iterating autonomously

This approximates a hybrid between:

• Devin
• Cursor

running fully local using:

• Ollama

---

# END
