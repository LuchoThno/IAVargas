"""
Project Creator - Creador de Proyectos
=====================================
Sistema de generación de proyectos en múltiples lenguajes:
- Python (Flask, Django, FastAPI, CLI)
- JavaScript/TypeScript (React, Vue, Node.js)
- Java (Spring Boot, Console)
- C# (.NET)
- Go
- Rust

Características:
- Templates predefinidos
- Estructuras de proyecto completas
- Configuración básica incluida
"""

import os
import shutil
from typing import Dict, Any, Optional
from pathlib import Path
import ollama

# ============================================
# CONFIGURACIÓN
# ============================================

MODEL = "llama3"

# Directorio de proyectos
PROJECTS_DIR = Path("workspace/projects")

# Templates de proyectos
PROJECT_TEMPLATES = {
    # Frontend Templates
    "html": {
        "basic": {
            "name": "HTML5 Basic",
            "description": "Página HTML5 básica",
            "files": {
                "index.html": '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Página</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Bienvenido</h1>
    </header>
    <main>
        <section class="hero">
            <h2>Hero Section</h2>
            <p>Contenido principal aquí</p>
        </section>
    </main>
    <footer>
        <p>&copy; 2024 Mi Sitio</p>
    </footer>
</body>
</html>''',
                "styles.css": '''/* Basic Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

header {
    background: #2c3e50;
    color: white;
    padding: 1rem;
    text-align: center;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

footer {
    background: #34495e;
    color: white;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}'''
            }
        },
        "tailwind": {
            "name": "HTML5 + Tailwind",
            "description": "Página con Tailwind CSS",
            "files": {
                "index.html": '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Página</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <header class="bg-blue-600 text-white p-4">
        <h1 class="text-3xl font-bold text-center">Bienvenido</h1>
    </header>
    <main class="max-w-4xl mx-auto p-4">
        <section class="bg-white rounded-lg shadow-md p-6 mb-4">
            <h2 class="text-2xl font-semibold mb-4">Hero Section</h2>
            <p class="text-gray-700">Contenido principal aquí</p>
        </section>
    </main>
    <footer class="bg-gray-800 text-white text-center p-4 mt-8">
        <p>&copy; 2024 Mi Sitio</p>
    </footer>
</body>
</html>''',
                "README.md": "# HTML + Tailwind\n\nAbre index.html en tu navegador"
            }
        },
        "responsive": {
            "name": "Responsive Layout",
            "description": "Layout responsive con Grid y Flexbox",
            "files": {
                "index.html": '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive Layout</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar">
        <div class="logo">Logo</div>
        <ul class="nav-links">
            <li><a href="#">Inicio</a></li>
            <li><a href="#">Acerca</a></li>
            <li><a href="#">Servicios</a></li>
            <li><a href="#">Contacto</a></li>
        </ul>
    </nav>
    <main class="container">
        <div class="grid">
            <article class="card">Contenido 1</article>
            <article class="card">Contenido 2</article>
            <article class="card">Contenido 3</article>
            <article class="card">Contenido 4</article>
        </div>
    </main>
    <footer class="footer">
        <p>&copy; 2024</p>
    </footer>
</body>
</html>''',
                "styles.css": '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: system-ui, sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.navbar {
    background: #1a1a2e;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-links {
    list-style: none;
    display: flex;
    gap: 1.5rem;
}

.nav-links a {
    color: white;
    text-decoration: none;
}

.container {
    flex: 1;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    width: 100%;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.footer {
    background: #1a1a2e;
    color: white;
    text-align: center;
    padding: 1rem;
}

@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 1rem;
    }
    
    .nav-links {
        flex-direction: column;
        align-items: center;
    }
}'''
            }
        },
        "landing": {
            "name": "Landing Page",
            "description": "Landing page moderna",
            "files": {
                "index.html": '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Landing Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar">
        <div class="logo">Brand</div>
        <div class="nav-links">
            <a href="#features">Características</a>
            <a href="#pricing">Precios</a>
            <a href="#contact" class="btn-primary">Contacto</a>
        </div>
    </nav>
    
    <section class="hero">
        <div class="hero-content">
            <h1>Construye algo increíble</h1>
            <p>La mejor solución para tu negocio</p>
            <a href="#get-started" class="btn-cta">Comenzar</a>
        </div>
    </section>
    
    <section id="features" class="features">
        <h2>Características</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <h3>Rápido</h3>
                <p>Optimizado para máximo rendimiento</p>
            </div>
            <div class="feature-card">
                <h3>Seguro</h3>
                <p>Protección de nivel empresarial</p>
            </div>
            <div class="feature-card">
                <h3>Escalable</h3>
                <p>Crece sin límites</p>
            </div>
        </div>
    </section>
    
    <footer class="footer">
        <p>&copy; 2024 Tu Empresa</p>
    </footer>
</body>
</html>''',
                "styles.css": ''':root {
    --primary: #3b82f6;
    --dark: #1e293b;
    --light: #f8fafc;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: var(--dark);
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 5%;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary);
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.nav-links a {
    text-decoration: none;
    color: var(--dark);
}

.btn-primary {
    background: var(--primary);
    color: white !important;
    padding: 0.5rem 1.5rem;
    border-radius: 6px;
}

.hero {
    background: linear-gradient(135deg, var(--primary), #1e40af);
    color: white;
    text-align: center;
    padding: 6rem 1rem;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.btn-cta {
    display: inline-block;
    background: white;
    color: var(--primary);
    padding: 1rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: transform 0.2s;
}

.btn-cta:hover {
    transform: translateY(-2px);
}

.features {
    padding: 4rem 5%;
    background: var(--light);
}

.features h2 {
    text-align: center;
    margin-bottom: 3rem;
    font-size: 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
}

.feature-card h3 {
    color: var(--primary);
    margin-bottom: 0.5rem;
}

.footer {
    background: var(--dark);
    color: white;
    text-align: center;
    padding: 2rem;
}'''
            }
        },
        "dashboard": {
            "name": "Admin Dashboard",
            "description": "Dashboard de administración",
            "files": {
                "index.html": '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <aside class="sidebar">
        <div class="logo">Admin Panel</div>
        <nav>
            <a href="#" class="active">Dashboard</a>
            <a href="#">Usuarios</a>
            <a href="#">Productos</a>
            <a href="#">Órdenes</a>
            <a href="#">Configuración</a>
        </nav>
    </aside>
    
    <main class="main-content">
        <header class="top-bar">
            <h1>Dashboard</h1>
            <div class="user">Admin</div>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Usuarios</h3>
                <p class="number">1,234</p>
            </div>
            <div class="stat-card">
                <h3>Ventas</h3>
                <p class="number">$12,345</p>
            </div>
            <div class="stat-card">
                <h3>Órdenes</h3>
                <p class="number">89</p>
            </div>
        </div>
        
        <div class="content">
            <div class="card">
                <h2>Actividad Reciente</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Usuario</th>
                            <th>Acción</th>
                            <th>Fecha</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Juan</td><td>Login</td><td>Ahora</td></tr>
                        <tr><td>María</td><td>Compra</td><td>Hace 5 min</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</body>
</html>''',
                "styles.css": '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    display: flex;
    font-family: system-ui, sans-serif;
    min-height: 100vh;
}

.sidebar {
    width: 250px;
    background: #1e293b;
    color: white;
    padding: 1rem;
    position: fixed;
    height: 100%;
}

.sidebar .logo {
    font-size: 1.5rem;
    font-weight: bold;
    padding: 1rem;
    border-bottom: 1px solid #334155;
    margin-bottom: 1rem;
}

.sidebar nav a {
    display: block;
    color: #94a3b8;
    text-decoration: none;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    margin-bottom: 0.25rem;
}

.sidebar nav a:hover,
.sidebar nav a.active {
    background: #334155;
    color: white;
}

.main-content {
    flex: 1;
    margin-left: 250px;
    background: #f1f5f9;
    min-height: 100vh;
}

.top-bar {
    background: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-card h3 {
    color: #64748b;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

.stat-card .number {
    font-size: 2rem;
    font-weight: bold;
    color: #0f172a;
}

.content {
    padding: 0 2rem 2rem;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.card h2 {
    margin-bottom: 1rem;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}

th {
    background: #f8fafc;
    font-weight: 600;
}'''
            }
        }
    },
    
    # JavaScript/TypeScript Templates
    "javascript": {
        "flask": {
            "name": "Flask Web App",
            "description": "Aplicación web con Flask",
            "files": {
                "app.py": '''"""Flask Application"""
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    app.run(debug=True)
''',
                "requirements.txt": "flask>=2.0.0\nflask-cors>=3.0.0\n",
                "templates/index.html": '''<!DOCTYPE html>
<html>
<head>
    <title>Flask App</title>
</head>
<body>
    <h1>Hello from Flask!</h1>
</body>
</html>''',
                "static/style.css": "body { font-family: Arial; }"
            }
        },
        "fastapi": {
            "name": "FastAPI REST API",
            "description": "API REST con FastAPI",
            "files": {
                "main.py": '''"""FastAPI Application"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/items/")
def create_item(item: Item):
    return {"item": item, "tax": item.price * 0.1 if item.tax is None else item.tax}
''',
                "requirements.txt": "fastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0\n"
            }
        },
        "cli": {
            "name": "CLI Tool",
            "description": "Herramienta de línea de comandos",
            "files": {
                "main.py": '''"""CLI Tool"""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Mi CLI Tool')
    parser.add_argument('--name', default='World', help='Nombre a saludar')
    parser.add_argument('--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    message = f"Hello, {args.name}!"
    if args.verbose:
        print(f"[DEBUG] Generando mensaje: {message}")
    print(message)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
''',
                "requirements.txt": "argparse\n",
                "README.md": "# CLI Tool\n\nUsage: python main.py --name TuNombre"
            }
        },
        "django": {
            "name": "Django Project",
            "description": "Proyecto Django completo",
            "files": {
                "manage.py": '#!/usr/bin/env python\nimport os\nimport sys\n\nif __name__ == "__main__":\n    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")\n    from django.core.management import execute_from_command_line\n    execute_from_command_line(sys.argv)\n',
                "project/__init__.py": "",
                "project/settings.py": """\"\"\"Django settings\"\"\"
import os

SECRET_KEY = 'django-insecure-change-this'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = ['django.contrib.contenttypes', 'django.contrib.staticfiles']
""",
                "project/urls.py": """\"\"\"URL Configuration\"\"\"
from django.urls import path
from . import views

urlpatterns = [path('', views.index, name='index')]
""",
                "project/views.py": """\"\"\"Views\"\"\"
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello from Django!\")
"""
            }
        }
    },
    "javascript": {
        "express": {
            "name": "Express.js API",
            "description": "API REST con Express.js",
            "files": {
                "index.js": '''const express = require("express");
const app = express();
const port = 3000;

app.use(express.json());

app.get("/", (req, res) => {
  res.json({ message: "Hello from Express!" });
});

app.get("/api/users", (req, res) => {
  res.json([{ id: 1, name: "John" }, { id: 2, name: "Jane" }]);
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
''',
                "package.json": '''{
  "name": "express-api",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0"
  }
}
'''
            }
        },
        "node-cli": {
            "name": "Node.js CLI",
            "description": "Herramienta CLI con Node.js",
            "files": {
                "cli.js": '''#!/usr/bin/env node

const args = process.argv.slice(2);

function main() {
  const command = args[0];
  
  switch(command) {
    case "hello":
      console.log("Hello, World!");
      break;
    case "help":
      console.log("Available commands: hello, help");
      break;
    default:
      console.log("Unknown command. Run: cli.js help");
  }
}

main();
''',
                "package.json": '''{
  "name": "my-cli",
  "version": "1.0.0",
  "bin": {
    "my-cli": "./cli.js"
  }
}
'''
            }
        }
    },
    "typescript": {
        "express-ts": {
            "name": "Express.js with TypeScript",
            "description": "API REST con Express y TypeScript",
            "files": {
                "src/index.ts": '''import express, { Request, Response } from "express";

const app = express();
const port = 3000;

app.use(express.json());

app.get("/", (req: Request, res: Response) => {
  res.json({ message: "Hello from Express TypeScript!" });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
''',
                "package.json": '''{
  "name": "express-ts",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.9.0"
  }
}
''',
                "tsconfig.json": '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
'''
            }
        }
    },
    "java": {
        "console": {
            "name": "Java Console App",
            "description": "Aplicación de consola Java",
            "files": {
                "src/Main.java": '''public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
''',
                "README.md": "# Java Console App\n\nCompile: javac src/Main.java\nRun: java -cp src Main"
            }
        }
    },
    "go": {
        "http": {
            "name": "Go HTTP Server",
            "description": "Servidor HTTP con Go",
            "files": {
                "main.go": '''package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello from Go!")
    })
    
    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
''',
                "go.mod": '''module myapp

go 1.21
'''
            }
        }
    },
    "rust": {
        "cli": {
            "name": "Rust CLI",
            "description": "Herramienta CLI con Rust",
            "files": {
                "src/main.rs": '''use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    match args.get(1).map(|s| s.as_str()) {
        Some("hello") => println!("Hello from Rust!"),
        Some("help") => println!("Commands: hello, help"),
        _ => println!("Unknown command"),
    }
}
''',
                "Cargo.toml": '''[package]
name = "my-cli"
version = "0.1.0"
edition = "2021"

[dependencies]
'''
            }
        }
    }
}

# ============================================
# CREADOR DE PROYECTOS
# ============================================

class ProjectCreator:
    """Creador de proyectos multi-lenguaje"""
    
    def __init__(self, projects_dir: str = None, model: str = MODEL):
        self.projects_dir = Path(projects_dir) if projects_dir else PROJECTS_DIR
        self.model = model
        self._ensure_projects_dir()
    
    def _ensure_projects_dir(self):
        """Asegura que el directorio de proyectos exista"""
        self.projects_dir.mkdir(parents=True, exist_ok=True)
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """Lista todas las plantillas disponibles"""
        return PROJECT_TEMPLATES
    
    def list_languages(self) -> list:
        """Lista los lenguajes disponibles"""
        return list(PROJECT_TEMPLATES.keys())
    
    def list_project_types(self, language: str) -> list:
        """Lista los tipos de proyecto para un lenguaje"""
        templates = PROJECT_TEMPLATES.get(language.lower(), {})
        return [
            {
                "id": key,
                "name": value["name"],
                "description": value["description"]
            }
            for key, value in templates.items()
        ]
    
    def create(self, name: str, template: str, language: str = "python") -> Dict[str, Any]:
        """
        Crea un proyecto desde una plantilla
        
        Args:
            name: Nombre del proyecto
            template: Identificador de la plantilla
            language: Lenguaje de programación
            
        Returns:
            Diccionario con el resultado
        """
        # Normalizar
        language = language.lower()
        
        # Buscar plantilla
        templates = PROJECT_TEMPLATES.get(language, {})
        template_data = templates.get(template.lower())
        
        if not template_data:
            return {
                "success": False,
                "error": f"Plantilla no encontrada: {template} para {language}",
                "available": list(templates.keys())
            }
        
        # Crear directorio del proyecto
        project_dir = self.projects_dir / name.lower().replace(" ", "_")
        
        if project_dir.exists():
            return {
                "success": False,
                "error": f"El proyecto {name} ya existe",
                "path": str(project_dir)
            }
        
        try:
            project_dir.mkdir(parents=True)
            
            # Crear archivos
            files = template_data.get("files", {})
            for file_path, content in files.items():
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            return {
                "success": True,
                "name": name,
                "template": template,
                "language": language,
                "path": str(project_dir),
                "files": list(files.keys())
            }
        except Exception as e:
            # Limpiar en caso de error
            if project_dir.exists():
                shutil.rmtree(project_dir)
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate(self, description: str, language: str = "python",
                project_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Genera código basado en descripción usando IA
        
        Args:
            description: Descripción de lo que se quiere generar
            language: Lenguaje de programación
            project_type: Tipo de proyecto opcional
            
        Returns:
            Código generado
        """
        prompt = f"""Eres un experto desarrollador en {language}.
Genera código base para un proyecto con la siguiente descripción:

Descripción: {description}
"""
        
        if project_type:
            prompt += f"Tipo de proyecto: {project_type}\n"
        
        prompt += """
Genera:
1. Estructura de archivos necesaria
2. Código principal
3. requirements.txt o package.json según corresponda

Responde en formato JSON:
{
  "files": {
    "nombre_archivo": "contenido del archivo"
  },
  "description": "breve descripción del proyecto",
  "instructions": ["instrucción 1", "instrucción 2"]
}
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"]
            
            # Intentar parsear JSON
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Crear proyecto
                project_name = description.split()[0].lower().replace(" ", "_")
                project_dir = self.projects_dir / project_name
                project_dir.mkdir(parents=True, exist_ok=True)
                
                files_created = []
                for file_path, file_content in data.get("files", {}).items():
                    full_path = project_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(file_content)
                    files_created.append(file_path)
                
                return {
                    "success": True,
                    "name": project_name,
                    "path": str(project_dir),
                    "files": files_created,
                    "description": data.get("description", ""),
                    "instructions": data.get("instructions", [])
                }
            
            return {
                "success": False,
                "error": "No se pudo parsear la respuesta",
                "raw": content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project_path(self, name: str) -> Optional[Path]:
        """Obtiene la ruta de un proyecto"""
        project_path = self.projects_dir / name.lower().replace(" ", "_")
        return project_path if project_path.exists() else None
    
    def list_projects(self) -> list:
        """Lista todos los proyectos creados"""
        if not self.projects_dir.exists():
            return []
        
        projects = []
        for item in self.projects_dir.iterdir():
            if item.is_dir():
                files = [f.name for f in item.rglob("*") if f.is_file()]
                projects.append({
                    "name": item.name,
                    "path": str(item),
                    "files": len(files)
                })
        return projects


# Instancia global
project_creator = ProjectCreator()


def create_project(name: str, template: str, language: str = "python") -> Dict[str, Any]:
    """Función de conveniencia para crear proyectos"""
    return project_creator.create(name, template, language)


def generate_code(description: str, language: str = "python") -> Dict[str, Any]:
    """Función de conveniencia para generar código"""
    return project_creator.generate(description, language)

