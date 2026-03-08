"""
Code Analyzer - Analizador de Código
====================================
Sistema de análisis de código para detectar:
- Vulnerabilidades de seguridad
- Code smells
- Complejidad ciclomática
- Sugerencias de mejora
- Mejores prácticas
- Documentación faltante
"""

import ast
import re
from typing import Dict, Any, List, Optional
import ollama

# ============================================
# CONFIGURACIÓN
# ============================================

MODEL = "llama3"

# Patrones de vulnerabilidades comunes
SECURITY_PATTERNS = {
    "python": [
        (r"eval\s*\(", "Uso de eval() - riesgo de inyección de código"),
        (r"exec\s*\(", "Uso de exec() - riesgo de inyección de código"),
        (r"pickle\.loads?\(", "Carga de pickle no segura - usar json"),
        (r"subprocess\.call\s*\(\s*['\"]", "Posible inyección de comandos - usar shell=False"),
        (r"os\.system\s*\(", "os.system es inseguro - usar subprocess"),
        (r"input\s*\(", "input() puede ser inseguro - validar entrada"),
        (r"open\s*\([^)]*['\"]w['\"][^)]*\)", "Escritura de archivos - validar path"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Contraseña hardcoded - usar variables de entorno"),
        (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "API key hardcoded - usar variables de entorno"),
        (r"sql\s*\+\s*['\"]", "Posible SQL injection - usar parámetros"),
        (r"\.format\s*\([^)]*%s", "Posible inyección - usar f-strings o parámetros"),
    ],
    "javascript": [
        (r"eval\s*\(", "Uso de eval() - riesgo de XSS"),
        (r"innerHTML\s*=", "innerHTML puede causar XSS - usar textContent"),
        (r"document\.write\s*\(", "document.write es inseguro"),
        (r"eval\s*\(", "eval permite inyección de código"),
        (r"new\s+Function\s*\(", "Function constructor es inseguro"),
    ],
    "java": [
        (r"Runtime\.getRuntime\(\)\.exec", "Ejecución de comandos insegura"),
        (r"Statement\.execute\s*\(", "SQL injection posible - usar PreparedStatement"),
        (r"ObjectInputStream", "Deserialización insegura"),
    ],
}

# ============================================
# ANALIZADOR DE CÓDIGO
# ============================================

class CodeAnalyzer:
    """Analizador de código multi-lenguaje"""
    
    def __init__(self, model: str = MODEL):
        self.model = model
    
    def analyze(self, code: str, language: str = "python", 
                check_security: bool = True, 
                check_complexity: bool = True) -> Dict[str, Any]:
        """
        Analiza código de forma completa
        
        Args:
            code: Código a analizar
            language: Lenguaje de programación
            check_security: Incluir análisis de seguridad
            check_complexity: Incluir análisis de complejidad
            
        Returns:
            Diccionario con resultados del análisis
        """
        result = {
            "language": language,
            "lines": len(code.splitlines()),
            "issues": [],
            "security_issues": [],
            "complexity": {},
            "suggestions": [],
            "score": 100
        }
        
        # Análisis de seguridad
        if check_security:
            security_issues = self._check_security(code, language)
            result["security_issues"] = security_issues
            result["issues"].extend(security_issues)
            result["score"] -= len(security_issues) * 10
        
        # Análisis de complejidad
        if check_complexity and language == "python":
            complexity = self._analyze_complexity(code)
            result["complexity"] = complexity
            if complexity.get("cyclomatic", 0) > 10:
                result["issues"].append({
                    "type": "complexity",
                    "message": f"Complejidad ciclomática alta: {complexity['cyclomatic']}"
                })
                result["score"] -= 5
        
        # Análisis con IA
        ai_analysis = self._ai_analyze(code, language)
        result["suggestions"] = ai_analysis.get("suggestions", [])
        
        # Score final
        result["score"] = max(0, result["score"])
        
        return result
    
    def _check_security(self, code: str, language: str) -> List[Dict[str, str]]:
        """Detecta problemas de seguridad en el código"""
        issues = []
        patterns = SECURITY_PATTERNS.get(language, [])
        
        for pattern, message in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "message": message,
                    "pattern": pattern
                })
        
        return issues
    
    def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analiza la complejidad del código"""
        try:
            tree = ast.parse(code)
            
            # Contar estructuras de control
            cyclomatic = 1  # Base
            functions = 0
            classes = 0
            imports = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    cyclomatic += 1
                elif isinstance(node, (ast.BoolOp,)):
                    cyclomatic += len(node.values) - 1
                elif isinstance(node, ast.FunctionDef):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports += 1
            
            return {
                "cyclomatic": cyclomatic,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "lines": len(code.splitlines())
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _ai_analyze(self, code: str, language: str) -> Dict[str, Any]:
        """Usa IA para analizar el código"""
        prompt = f"""Analiza el siguiente código en {language} y proporciona:
1. Una lista de sugerencias de mejora
2. Posibles problemas o code smells

Código:
```{language}
{code}
```

Responde en formato JSON con:
{{"suggestions": ["sugerencia1", "sugerencia2", ...]}}"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Intentar parsear JSON de la respuesta
            content = response["message"]["content"]
            # Extraer JSON si está envuelto en markdown
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            return {"suggestions": [content]}
        except Exception as e:
            return {"suggestions": [], "error": str(e)}
    
    def refactor(self, code: str, language: str = "python", 
                 style: str = "default", goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Refactoriza el código según el objetivo
        
        Args:
            code: Código a refactorizar
            language: Lenguaje de programación
            style: Estilo de refactorización
            goal: Objetivo específico
        """
        prompt = f"""Eres un experto refactorizador de código {language}.
Tu tarea es refactorizar el siguiente código.

Estilo: {style}
Objetivo: {goal or "mejorar calidad general"}

Código original:
```{language}
{code}
```

Proporciona:
1. Código refactorizado
2. Lista de cambios realizados
3. Explicación breve de cada cambio

Responde en formato JSON:
{{"refactored_code": "...", "changes": ["cambio1", "cambio2", ...], "explanation": "..."}}"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"]
            
            # Extraer código refactorizado
            code_match = re.search(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
            refactored = code_match.group(1) if code_match else code
            
            return {
                "refactored_code": refactored,
                "full_response": content,
                "style": style,
                "goal": goal
            }
        except Exception as e:
            return {"error": str(e)}
    
    def generate_tests(self, code: str, language: str = "python",
                      framework: Optional[str] = None, count: int = 3) -> Dict[str, Any]:
        """
        Genera tests unitarios para el código
        
        Args:
            code: Código para generar tests
            language: Lenguaje de programación
            framework: Framework de testing
            count: Número de tests a generar
        """
        framework = framework or self._get_default_framework(language)
        
        prompt = f"""Eres un experto en testing en {language}.
Tu tarea es generar {count} tests unitarios usando {framework}.

Código a testear:
```{language}
{code}
```

Genera tests que:
- Cubran casos normales
- Cubran casos extremos
- Sean independientes entre sí
- Usen aserciones claras

Responde en formato JSON:
{{"tests": "...código de los tests...", "framework": "{framework}", "coverage": ["test1", "test2", ...]}}"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"]
            
            # Extraer código de tests
            code_match = re.search(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
            tests = code_match.group(1) if code_match else content
            
            return {
                "tests": tests,
                "framework": framework,
                "language": language,
                "full_response": content
            }
        except Exception as e:
            return {"error": str(e)}
    
    def debug(self, code: str, language: str = "python",
             error_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Analiza y corrige errores en el código
        
        Args:
            code: Código con errores
            language: Lenguaje de programación
            error_message: Mensaje de error opcional
        """
        prompt = f"""Eres un experto depurador en {language}.
Tu tarea es encontrar y corregir errores en el siguiente código.

"""
        
        if error_message:
            prompt += f"Error proporcionado: {error_message}\n"
        
        prompt += f"""Código:
```{language}
{code}
```

Proporciona:
1. Análisis del posible error
2. Código corregido
3. Explicación de la solución

Responde en formato JSON:
{{"analysis": "...", "fixed_code": "...", "explanation": "..."}}"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"]
            
            # Extraer código corregido
            code_match = re.search(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
            fixed = code_match.group(1) if code_match else code
            
            return {
                "fixed_code": fixed,
                "analysis": content,
                "language": language
            }
        except Exception as e:
            return {"error": str(e)}
    
    def optimize(self, code: str, language: str = "python",
                focus: str = "performance") -> Dict[str, Any]:
        """
        Optimiza el código para mejor rendimiento
        
        Args:
            code: Código a optimizar
            language: Lenguaje de programación
            focus: Área de enfoque (performance, memory, readability)
        """
        prompt = f"""Eres un experto en optimización de código {language}.
Tu tarea es optimizar el siguiente código.

Enfoque: {focus}

Código original:
```{language}
{code}
```

Proporciona:
1. Código optimizado
2. Lista de optimizaciones realizadas
3. Mejora esperada

Responde en formato JSON:
{{"optimized_code": "...", "optimizations": ["opt1", "opt2", ...], "expected_improvement": "..."}}"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"]
            
            # Extraer código optimizado
            code_match = re.search(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
            optimized = code_match.group(1) if code_match else code
            
            return {
                "optimized_code": optimized,
                "full_response": content,
                "focus": focus
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_default_framework(self, language: str) -> str:
        """Obtiene el framework de testing por defecto"""
        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "java": "junit",
            "typescript": "jest",
            "go": "testing",
            "rust": "#[test]"
        }
        return frameworks.get(language, "pytest")

