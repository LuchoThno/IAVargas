"""
Diagnostico de Ollama
=====================
"""
import subprocess
import sys
import time

print("=" * 50)
print("DIAGNOSTICO DE OLLAMA")
print("=" * 50)

# 1. Verificar si Ollama está corriendo
print("\n1. Verificando proceso de Ollama...")
result = subprocess.run(["tasklist"], capture_output=True, text=True)
if "ollama.exe" in result.stdout:
    print("   ✓ Ollama está corriendo")
else:
    print("   ✗ Ollama NO está corriendo")
    print("   Iniciando Ollama...")
    subprocess.Popen(["ollama", "serve"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
    time.sleep(3)

# 2. Probar Ollama directamente
print("\n2. Probando Ollama directamente...")
try:
    result = subprocess.run(
        ["ollama", "list"], 
        capture_output=True, 
        text=True, 
        timeout=10
    )
    print(f"   Output: {result.stdout}")
    if result.stderr:
        print(f"   Error: {result.stderr}")
except Exception as e:
    print(f"   Error: {e}")

# 3. Probar API server
print("\n3. Probando API server...")
import requests
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    print(f"   ✓ API Server: {r.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 4. Probar endpoint /ask
print("\n4. Probando /ask...")
try:
    r = requests.post(
        "http://localhost:8000/ask",
        json={"prompt": "Di hola", "max_tokens": 20},
        timeout=30
    )
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 50)
print("FIN DEL DIAGNOSTICO")
print("=" * 50)

