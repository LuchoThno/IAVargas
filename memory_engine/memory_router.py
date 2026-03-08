"""
Memory Router - Clasificación de Tipos de Memoria
=================================================
IA Local Vargas - Memory Engine
Clasifica memorias en: episodic, semantic, procedural
"""

import re
from typing import Dict, List
from . import config


# Palabras clave para clasificación
ROUTING_RULES = {
    "episodic": [
        # Experiencias personales, eventos
        r"trabajo en",
        r"mi nombre es",
        r"soy (yo|luis|usuario)",
        r"estoy en",
        r"fui a",
        r"conocí a",
        r"me pasó",
        r"ayer",
        r"hoy",
        r"mañana",
        r"la semana pasada",
        r"el mes pasado",
        r"reunión con",
        r"hablé con",
        r"visité",
        r"trabajo como",
        r"empleo",
        r"puesto",
        r"cargo",
        r"empresa donde",
        r"trabajé",
        r"estudio",
        r" vivo en",
        r"mi ciudad",
        r"mi país",
        r"familia",
        r"hijos",
        r"esposa",
        r"esposo",
        r"padres",
    ],
    "semantic": [
        # Conocimiento, definiciones, datos
        r"qué es",
        r"explica",
        r"definición",
        r"significa",
        r"cómo funciona",
        r"cuál es el",
        r"cuáles son los",
        r"información sobre",
        r"sabes",
        r"conoces",
        r"dato",
        r"hecho",
        r"concepto",
        r"teoría",
        r"principio",
        r"historia",
        r"origen",
        r"significado",
        r"por qué",
        r"para qué",
        r"ventajas",
        r"desventajas",
        r"diferencia entre",
        r"comparar",
    ],
    "procedural": [
        # Procesos, procedimientos, pasos
        r"pasos para",
        r"cómo hacer",
        r"cómo crear",
        r"cómo instalar",
        r"cómo configurar",
        r"procedimiento",
        r"instrucciones",
        r"tutorial",
        r"guía",
        r"recipe",
        r"receta",
        r"proceso",
        r"flujo",
        r"pipeline",
        r"workflow",
        r"secuencia",
        r"etapas",
        r"fases",
        r"manual",
        r"documentación",
    ]
}


def classify_memory(text: str) -> str:
    """
    Clasifica el texto en un tipo de memoria
    Args:
        text: Texto a clasificar
    Returns:
        Tipo de memoria: 'episodic', 'semantic' o 'procedural'
    """
    text_lower = text.lower()
    
    scores = {
        "episodic": 0,
        "semantic": 0,
        "procedural": 0
    }
    
    # Aplicar reglas de clasificación
    for memory_type, patterns in ROUTING_RULES.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                scores[memory_type] += 1
    
    # Si no hay coincidencias, por defecto es episodic
    if all(score == 0 for score in scores.values()):
        return "episodic"
    
    # Retornar el tipo con mayor puntuación
    return max(scores, key=scores.get)


def get_memory_type_info(memory_type: str) -> str:
    """Retorna información sobre el tipo de memoria"""
    return config.MEMORY_TYPES.get(memory_type, "Desconocido")


def get_all_memory_types() -> List[str]:
    """Retorna todos los tipos de memoria disponibles"""
    return list(config.MEMORY_TYPES.keys())


def suggest_importance(text: str) -> int:
    """
    Sugiere un nivel de importancia basado en el contenido
    Args:
        text: Texto a analizar
    Returns:
        Importancia (1-5)
    """
    text_lower = text.lower()
    importance = 3  # Valor por defecto
    
    # Palabras que indican alta importancia
    high_importance_keywords = [
        "recordar", "importante", "no olvidar", "crucial",
        "esencial", "fundamental", "vital", "necesario",
        "me gusta", "no me gusta", "prefiero", "odio",
        "mi nombre", "soy", "tengo", "vivo en",
        "trabajo", "empresa", "jefe", "salario",
        "password", "contraseña", "cuenta", "acceso"
    ]
    
    # Palabras que indican baja importancia
    low_importance_keywords = [
        "tal vez", "quizás", "probablemente", "posiblemente",
        "no importa", "da igual", "da lo mismo"
    ]
    
    for keyword in high_importance_keywords:
        if keyword in text_lower:
            importance += 1
            break
    
    for keyword in low_importance_keywords:
        if keyword in text_lower:
            importance -= 1
            break
    
    # Asegurar que esté en el rango 1-5
    return max(1, min(5, importance))


def should_be_long_term(text: str, importance: int) -> bool:
    """
    Determina si una memoria debe ser de largo plazo
    Args:
        text: Texto de la memoria
        importance: Nivel de importancia (1-5)
    Returns:
        True si debe ser guardada a largo plazo
    """
    # Alta importancia siempre es largo plazo
    if importance >= 4:
        return True
    
    # Información personal/episódica importante
    text_lower = text.lower()
    personal_keywords = ["trabajo", "mi nombre", "vivo", "soy", "tengo", "familia"]
    
    if any(kw in text_lower for kw in personal_keywords):
        return importance >= 3
    
    return False

