"""
Orchestrator - Main decision engine
===================================
Coordinates all agents and manages the execution loop.
"""

import os
import json
from .planner import PlannerAgent
from .coder import CoderAgent
from .debugger import DebuggerAgent
from .tester import TestAgent
from .researcher import ResearchAgent
from .refactor import RefactorAgent


class Orchestrator:
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self, llm, file_tool, runner, max_iterations: int = 10):
        self.llm = llm
        self.file_tool = file_tool
        self.runner = runner
        self.max_iterations = max_iterations
        
        # Initialize all agents
        self.planner = PlannerAgent(llm)
        self.coder = CoderAgent(llm, file_tool)
        self.debugger = DebuggerAgent(llm)
        self.tester = TestAgent(llm)
        self.researcher = ResearchAgent(llm)
        self.refactor = RefactorAgent(llm)
        
        # Execution history
        self.history = []
    
    def execute(self, task: str, workspace: str = "ai_dev_system/workspace/projects") -> dict:
        """
        Execute a task from start to finish
        
        Args:
            task: Task description
            workspace: Directory for project files
        
        Returns:
            dict with execution results
        """
        self.history = []
        self._log(f"Starting task: {task}")
        
        # Step 1: Research
        self._log("Phase 1: Researching...")
        research = self.researcher.research(task)
        self._log(f"Research complete: {research[:200]}...")
        
        # Step 2: Plan
        self._log("Phase 2: Creating architecture plan...")
        plan = self.planner.plan(task)
        self._log(f"Plan: {json.dumps(plan, indent=2)}")
        
        # Step 3: Generate code
        self._log("Phase 3: Generating code...")
        files = self.coder.generate(task, plan, research)
        
        if "error" in files:
            self._log(f"Code generation error: {files}")
            return {"status": "error", "phase": "code_generation", "details": files}
        
        # Step 4: Save project
        self._log(f"Phase 4: Saving {len(files)} files...")
        save_result = self.coder.save_project(files, workspace)
        self._log(f"Saved: {save_result}")
        
        # Step 5: Generate tests
        self._log("Phase 5: Generating tests...")
        tests = self.tester.generate_tests(files)
        
        if "error" not in tests:
            test_files = {}
            for test_name, test_content in tests.items():
                if not test_name.startswith("_"):
                    test_files[test_name] = test_content
            
            if test_files:
                # Create tests directory
                test_dir = os.path.join(workspace, "tests")
                os.makedirs(test_dir, exist_ok=True)
                
                # Save test files
                for test_name, test_content in test_files.items():
                    test_path = os.path.join(workspace, test_name)
                    try:
                        with open(test_path, 'w', encoding='utf-8') as f:
                            f.write(test_content)
                        self._log(f"Saved test: {test_name}")
                    except Exception as e:
                        self._log(f"Error saving test {test_name}: {e}")
        
        # Step 6: Run project (with iteration for debugging)
        self._log("Phase 6: Running project...")
        
        run_command = plan.get("run_command", "python main.py")
        result = self.runner.run(f"cd {workspace} && {run_command}", timeout=120)
        
        iteration = 0
        while not result["success"] and iteration < self.max_iterations:
            iteration += 1
            self._log(f"Debug iteration {iteration}...")
            
            # Get error info
            error = result.get("stderr", result.get("stdout", "Unknown error"))
            self._log(f"Error: {error[:500]}")
            
            # Try to fix
            all_files = {**files}
            fixes = self.debugger.fix(error, all_files)
            
            if "error" in fixes:
                self._log(f"Debug failed: {fixes}")
                break
            
            # Apply fixes
            for filename, content in fixes.items():
                if filename.startswith("_") or filename in ["error", "raw_response"]:
                    continue
                
                filepath = os.path.join(workspace, filename)
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self._log(f"Applied fix to: {filename}")
                except Exception as e:
                    self._log(f"Error writing {filename}: {e}")
            
            # Re-run
            result = self.runner.run(f"cd {workspace} && {run_command}", timeout=120)
        
        # Step 7: Refactor if successful
        if result["success"]:
            self._log("Phase 7: Refactoring for quality...")
            refactored = self.refactor.refactor(files)
            
            # Save refactored files (optional - commented out to preserve working code)
            # for filename, content in refactored.items():
            #     if not filename.startswith("_"):
            #         filepath = os.path.join(workspace, filename)
            #         with open(filepath, 'w', encoding='utf-8') as f:
            #             f.write(content)
        
        # Final result
        final_result = {
            "status": "success" if result["success"] else "failed",
            "iterations": iteration + 1,
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "plan": plan,
            "history": self.history
        }
        
        self._log(f"Final status: {final_result['status']}")
        
        return final_result
    
    def execute_simple(self, task: str, workspace: str = "ai_dev_system/workspace/projects") -> str:
        """
        Simple execution - returns status string
        
        Args:
            task: Task description
            workspace: Directory for project files
        
        Returns:
            "SUCCESS" or "FAILED"
        """
        result = self.execute(task, workspace)
        
        if result["status"] == "success":
            return "SUCCESS"
        
        return f"FAILED after {result.get('iterations', 0)} iterations"
    
    def _log(self, message: str):
        """Log a message"""
        print(f"[Orchestrator] {message}")
        self.history.append(message)
    
    def get_history(self) -> list:
        """Get execution history"""
        return self.history


def create_orchestrator(model: str = "llama3", workspace: str = "ai_dev_system/workspace/projects") -> Orchestrator:
    """
    Create an orchestrator with default settings
    
    Args:
        model: LLM model name
        workspace: Workspace directory
    
    Returns:
        Orchestrator instance
    """
    from core.llm import LLMClient
    from core.tools import FileSystemTool
    from runtime.runner import Runner
    
    llm = LLMClient(model=model)
    file_tool = FileSystemTool(workspace)
    runner = Runner(workspace)
    
    return Orchestrator(llm, file_tool, runner)

