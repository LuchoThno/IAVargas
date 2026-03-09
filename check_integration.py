#!/usr/bin/env python3
"""
Quick check script to see the current state of integration
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("IA Vargas - Integration Status Check")
print("=" * 60)

# Check 1: Is api_server.py running?
print("\n1. Checking API Server...")
try:
    import requests
    r = requests.get("http://localhost:8000/health", timeout=3)
    health = r.json()
    print(f"   API Server: {health.get('status', 'unknown')}")
    print(f"   Model: {health.get('model', 'unknown')}")
except Exception as e:
    print(f"   API Server not responding: {e}")

# Check 2: Does api_server.py have orchestrate endpoint?
print("\n2. Checking Orchestrator endpoint in api_server.py...")
with open("api_server.py", "r", encoding="utf-8") as f:
    api_content = f.read()
    if "orchestrate" in api_content.lower():
        print("   Orchestrator endpoint found")
    else:
        print("   Orchestrator endpoint NOT found")

# Check 3: VSCode extension api.ts
print("\n3. Checking VSCode Extension (api.ts)...")
try:
    with open("vscode_extension/src/api.ts", "r", encoding="utf-8") as f:
        api_ts = f.read()
        if "orchestrate" in api_ts.lower():
            print("   orchestrate method found")
        else:
            print("   orchestrate method NOT found")
except Exception as e:
    print(f"   Error: {e}")

# Check 4: IntelliJ Plugin
print("\n4. Checking IntelliJ Plugin...")
try:
    with open("intellij_plugin/src/main/kotlin/com/iavargas/actions/OrchestrateAction.kt", "r", encoding="utf-8") as f:
        content = f.read()
        print("   OrchestrateAction.kt exists")
except FileNotFoundError:
    print("   OrchestrateAction.kt NOT found")

# Check 5: ai_dev_system orchestrator
print("\n5. Checking ai_dev_system...")
try:
    with open("ai_dev_system/agents/orchestrator.py", "r", encoding="utf-8") as f:
        content = f.read()
        print("   Orchestrator agent exists")
except FileNotFoundError:
    print("   Orchestrator agent NOT found")

print("\n" + "=" * 60)

