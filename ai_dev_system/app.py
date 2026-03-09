"""
AI Dev System - Main Entry Point
=================================
A Devin-like Autonomous Developer + Cursor-style AI Editor (Local)

This is a local AI software engineering system combining:
- Autonomous developer similar to Devin
- Interactive coding editor similar to Cursor
- Local LLM runtime via Ollama

Usage:
    python ai_dev_system/app.py
    python ai_dev_system/app.py --task "create a fastapi user API"
    python ai_dev_system/app.py --interactive
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm import LLMClient, get_default_client
from core.tools import FileSystemTool
from runtime.runner import Runner
from agents.orchestrator import Orchestrator
from editor.ai_commands import explain, refactor, add_tests, fix, improve


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Dev System - Local AI Software Engineer"
    )
    
    parser.add_argument(
        "--task", 
        type=str, 
        help="Task to execute"
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Start interactive mode"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="llama3",
        help="Ollama model to use"
    )
    
    parser.add_argument(
        "--workspace", 
        type=str, 
        default="ai_dev_system/workspace/projects",
        help="Workspace directory"
    )
    
    parser.add_argument(
        "--explain", 
        type=str,
        help="Explain code from file"
    )
    
    parser.add_argument(
        "--refactor", 
        type=str,
        help="Refactor code from file"
    )
    
    parser.add_argument(
        "--add-tests", 
        type=str,
        help="Add tests to code from file"
    )
    
    parser.add_argument(
        "--fix", 
        type=str,
        help="Fix errors in file"
    )
    
    parser.add_argument(
        "--error",
        type=str,
        default="",
        help="Error message for --fix"
    )
    
    args = parser.parse_args()
    
    # Create workspace directory
    os.makedirs(args.workspace, exist_ok=True)
    
    # Handle single commands
    if args.explain:
        code = open(args.explain, 'r', encoding='utf-8').read()
        result = explain(code)
        print(result)
        return
    
    if args.refactor:
        code = open(args.refactor, 'r', encoding='utf-8').read()
        result = refactor(code)
        print(result)
        return
    
    if args.add_tests:
        code = open(args.add_tests, 'r', encoding='utf-8').read()
        result = add_tests(code)
        print(result)
        return
    
    if args.fix:
        code = open(args.fix, 'r', encoding='utf-8').read()
        result = fix(code, args.error)
        print(result)
        return
    
    # Handle task execution
    if args.task:
        print(f"\n{'='*60}")
        print(f"AI Dev System - Executing Task")
        print(f"{'='*60}")
        print(f"Task: {args.task}")
        print(f"Model: {args.model}")
        print(f"Workspace: {args.workspace}")
        print(f"{'='*60}\n")
        
        # Initialize components
        llm = LLMClient(model=args.model)
        file_tool = FileSystemTool(args.workspace)
        runner = Runner(args.workspace)
        
        # Create orchestrator
        orchestrator = Orchestrator(llm, file_tool, runner)
        
        # Execute task
        result = orchestrator.execute(args.task, args.workspace)
        
        # Print results
        print(f"\n{'='*60}")
        print(f"Execution Results")
        print(f"{'='*60}")
        print(f"Status: {result['status']}")
        print(f"Iterations: {result.get('iterations', 1)}")
        
        if result['status'] == 'success':
            print(f"\n✓ Project created successfully!")
            print(f"Files saved to: {args.workspace}")
        else:
            print(f"\n✗ Project creation failed")
            print(f"Error: {result.get('error', 'Unknown')[:500]}")
        
        print(f"\nExecution History:")
        for i, log in enumerate(result.get('history', [])[-10:], 1):
            print(f"  {i}. {log[:100]}...")
        
        return
    
    # Interactive mode
    if args.interactive or not args.task:
        print(f"\n{'='*60}")
        print(f"AI Dev System - Interactive Mode")
        print(f"{'='*60}")
        print("Type 'help' for commands, 'exit' to quit")
        print()
        
        # Initialize components
        llm = LLMClient(model=args.model)
        file_tool = FileSystemTool(args.workspace)
        runner = Runner(args.workspace)
        orchestrator = Orchestrator(llm, file_tool, runner)
        
        while True:
            try:
                task = input("\nTask> ").strip()
                
                if not task:
                    continue
                
                if task.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if task.lower() == 'help':
                    print("""
Commands:
  create <task>    - Create a new project
  explain <file>   - Explain code in a file
  refactor <file>  - Refactor code in a file
  test <file>      - Add tests to a file
  fix <file>       - Fix errors in a file
  list             - List project files
  run              - Run the current project
  clear            - Clear workspace
  help             - Show this help
  exit             - Exit
""")
                    continue
                
                if task.lower().startswith('explain '):
                    filename = task[8:].strip()
                    if os.path.exists(filename):
                        code = open(filename, 'r', encoding='utf-8').read()
                        print(explain(code))
                    else:
                        print(f"File not found: {filename}")
                    continue
                
                if task.lower().startswith('refactor '):
                    filename = task[9:].strip()
                    if os.path.exists(filename):
                        code = open(filename, 'r', encoding='utf-8').read()
                        print(refactor(code))
                    else:
                        print(f"File not found: {filename}")
                    continue
                
                if task.lower().startswith('test '):
                    filename = task[5:].strip()
                    if os.path.exists(filename):
                        code = open(filename, 'r', encoding='utf-8').read()
                        print(add_tests(code))
                    else:
                        print(f"File not found: {filename}")
                    continue
                
                if task.lower().startswith('create '):
                    create_task = task[7:].strip()
                    result = orchestrator.execute(create_task, args.workspace)
                    
                    if result['status'] == 'success':
                        print(f"\n✓ Project created successfully!")
                    else:
                        print(f"\n✗ Failed: {result.get('error', 'Unknown')[:200]}")
                    continue
                
                if task.lower() == 'list':
                    files = file_tool.list_files()
                    print(f"Project files in {args.workspace}:")
                    for f in files:
                        print(f"  - {f}")
                    continue
                
                if task.lower() == 'run':
                    result = runner.run(f"python {args.workspace}/main.py")
                    print("Output:" if result['success'] else "Error:")
                    print(result.get('stdout', '') or result.get('stderr', ''))
                    continue
                
                if task.lower() == 'clear':
                    import shutil
                    if os.path.exists(args.workspace):
                        shutil.rmtree(args.workspace)
                    os.makedirs(args.workspace)
                    print("Workspace cleared")
                    continue
                
                # Default: treat as task
                result = orchestrator.execute(task, args.workspace)
                
                if result['status'] == 'success':
                    print(f"\n✓ Task completed successfully!")
                else:
                    print(f"\n✗ Task failed")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        return
    
    # Show help if no arguments
    parser.print_help()


if __name__ == "__main__":
    main()

