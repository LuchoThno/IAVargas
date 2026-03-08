"""
Main Script - Ejemplo de Uso del Memory Engine
===============================================
IA Local Vargas - Memory Engine
Ejemplo de uso completo del sistema de memoria
"""

from memory_engine import (
    init_db,
    save_memory,
    search_memory,
    get_all_memories,
    get_memory_stats,
    clean_old_memories,
    add_relation,
    get_related_memories,
    get_knowledge_graph_summary,
    format_search_results,
    get_retention_policy,
    get_important_memories
)


def main():
    """Función principal de demostración"""
    
    print("=" * 60)
    print("🤖 IA Local Vargas - Memory Engine Demo")
    print("=" * 60)
    
    # 1. Inicializar base de datos
    print("\n📦 Inicializando base de datos...")
    init_db()
    print("✓ Base de datos lista")
    
    # 2. Mostrar política de retención
    print("\n⚙️ Política de retención:")
    policy = get_retention_policy()
    print(f"  - Short-term: {policy['short_term_days']} días")
    print(f"  - Long-term: {policy['long_term_days']} días")
    print(f"  - Máximo memorias: {policy['max_memories']}")
    
    # 3. Guardar memorias de ejemplo
    print("\n💾 Guardando memorias de ejemplo...")
    
    # Memoria episódica - información personal
    mem1 = save_memory(
        "El usuario trabaja en el puerto de Talcahuano",
        importance=5
    )
    
    # Memoria semántica - conocimiento
    mem2 = save_memory(
        "Servasmar es una empresa de software marítimo",
        importance=4
    )
    
    # Memoria episódica - experiencia
    mem3 = save_memory(
        "Mi nombre es Luis Vargas y soy desarrollador de software",
        importance=5
    )
    
    # Memoria procedimental - proceso
    mem4 = save_memory(
        "Pasos para instalar Python: 1) Descargar installer, 2) Ejecutar, 3) Agregar al PATH",
        importance=3
    )
    
    # Más ejemplos
    mem5 = save_memory(
        "El usuario vive en Chile, específicamente en la región del Biobío",
        importance=4
    )
    
    mem6 = save_memory(
        "Python es un lenguaje de programación de alto nivel",
        importance=3
    )
    
    print(f"✓ {6} memorias guardadas")
    
    # 4. Crear relaciones en el grafo de conocimientos
    print("\n🔗 Creando relaciones...")
    
    if mem1 and mem2:
        add_relation(mem1, "works_at_company", mem2)
        print(f"  - Relación: trabaja en empresa → Servasmar")
    
    if mem3 and mem1:
        add_relation(mem3, "person_works_at", mem1)
        print(f"  - Relación: persona → lugar de trabajo")
    
    # 5. Búsqueda de ejemplo
    print("\n" + "=" * 60)
    print("🔍 EJEMPLOS DE BÚSQUEDA")
    print("=" * 60)
    
    # Consulta 1
    query1 = "donde trabaja el usuario"
    print(f"\n📝 Consulta: '{query1}'")
    results1 = search_memory(query1, n_results=3)
    print(format_search_results(results1))
    
    # Consulta 2
    query2 = "empresa de software"
    print(f"\n📝 Consulta: '{query2}'")
    results2 = search_memory(query2, n_results=3)
    print(format_search_results(results2))
    
    # Consulta 3
    query3 = "lenguaje de programación"
    print(f"\n📝 Consulta: '{query3}'")
    results3 = search_memory(query3, n_results=3)
    print(format_search_results(results3))
    
    # 6. Mostrar grafo de conocimientos
    print("\n" + "=" * 60)
    print("🕸️ GRAFO DE CONOCIMIENTOS")
    print("=" * 60)
    
    graph_summary = get_knowledge_graph_summary()
    print(f"\nEstadísticas del grafo:")
    print(f"  - Total memorias: {graph_summary['total_memories']}")
    print(f"  - Total relaciones: {graph_summary['total_relations']}")
    print(f"  - Memorias con relaciones: {graph_summary['memories_with_relations']}")
    
    if graph_summary['most_common_relations']:
        print("\nTipos de relaciones más comunes:")
        for rel_type, count in graph_summary['most_common_relations']:
            print(f"  - {rel_type}: {count}")
    
    # 7. Mostrar memorias importantes
    print("\n" + "=" * 60)
    print("⭐ MEMORIAS IMPORTANTES")
    print("=" * 60)
    
    important = get_important_memories(min_importance=4, n_results=10)
    for mem in important:
        type_emoji = {"episodic": "📍", "semantic": "📚", "procedural": "⚙️"}.get(mem.get("memory_type"), "📝")
        print(f"{type_emoji} ⭐{mem['importance']}: {mem['text']}")
    
    # 8. Estadísticas finales
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 60)
    
    stats = get_memory_stats()
    print(f"\nTotal de memorias: {stats['total']}")
    
    if stats['by_type']:
        print("\nPor tipo:")
        for mem_type, count in stats['by_type'].items():
            print(f"  - {mem_type}: {count}")
    
    if stats['by_importance']:
        print("\nPor importancia:")
        for imp, count in sorted(stats['by_importance'].items()):
            print(f"  - {'⭐' * imp} ({imp}): {count}")
    
    print(f"\nImportancia promedio: {stats['average_importance']}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completada exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    main()

