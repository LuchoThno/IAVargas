"""
Diagnostico de Ollama - Version corregida
=========================================
"""
import subprocess
import sys
import os

# Fix encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
import requests
import json

print("=" * 50)
print("DIAGNOSTICO DE OLLAMA")
print("=" * 50)

# 1. Verificar si Ollama esta corriendo
print("\n1. Verificando proceso de Ollama...")
result = subprocess.run(["tasklist"], capture_output=True, text=True)
if "ollama.exe" in result.stdout:
    print("   OK: Ollama esta corriendo")
else:
    print("   ERROR: Ollama NO esta corriendo")

# 2. Probar API server
print("\n2. Probando API server...")
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    print("   OK: API Server: " + json.dumps(r.json()))
except Exception as e:
    print("   ERROR: " + str(e))

# 3. Probar endpoint /ask
print("\n3. Probando /ask...")
try:
    r = requests.post(
        "http://localhost:8000/ask",
        json={"prompt": "Di hola", "max_tokens": 20},
        timeout=30
    )
    print("   Status: " + str(r.status_code))
    data = r.json()
    if data.get('success'):
        print("   OK: " + data.get('result'))
    else:
        print("   ERROR: " + data.get('error'))
except Exception as e:
    print("   ERROR: " + str(e))

print("\n" + "=" * 50)
print("FIN DEL DIAGNOSTICO")
print("=" * 50)

