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
    "python": {
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

