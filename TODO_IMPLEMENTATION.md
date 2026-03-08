# TODO: Implementación de Mejoras - IA Local Vargas 

MEJORA DEL SISTEMA DE GESTIÓN DE DOCUMENTOS Y RAG
=================================================

Objetivo
--------
Mejorar el sistema actual de procesamiento de documentos, embeddings y búsqueda semántica (RAG) para hacerlo más:
- Escalable
- Eficiente
- Seguro
- Modular
- Preparado para producción

El sistema actual ya procesa:
- PDFs
- CSV
- Excel
- TXT

También implementa:
- Chunking de texto
- Generación de embeddings con sentence-transformers
- Búsqueda semántica con similaridad coseno
- Sistema de caché
- RAG básico

Sin embargo, se requieren mejoras importantes.

Tareas a realizar
-----------------

1. Optimización de carga del modelo
Reemplazar la carga global del modelo:

    doc_model = SentenceTransformer("all-MiniLM-L6-v2")

Por un sistema de carga lazy:

- El modelo debe cargarse solo cuando sea necesario.
- Debe existir una función `get_model()` que maneje la inicialización.
- Evitar cargar el modelo durante el import del módulo.

2. Optimizar cálculo de hash de archivos
El hash actual lee el archivo completo en memoria.

Implementar hashing por bloques para soportar archivos grandes:

- Leer archivos en chunks de 8KB o 16KB.
- Evitar cargar archivos completos en RAM.

3. Mejorar sistema de chunking
El chunking actual está basado en caracteres.

Mejorarlo para:

- Mantener coherencia semántica
- Dividir preferentemente por:
    - párrafos
    - oraciones
- Mantener overlap configurable
- Evitar fragmentar frases.

4. Optimizar generación de embeddings
Actualmente se generan embeddings sin batching optimizado.

Mejorar:
- usar batch_size configurable
- usar numpy arrays
- reducir conversiones innecesarias

5. Vectorizar el cálculo de similaridad
Actualmente el cálculo de similaridad coseno se realiza en loops.

Optimizar usando operaciones vectorizadas con numpy.

Evitar loops innecesarios cuando se comparan embeddings.

6. Implementar índice vectorial
Agregar soporte para base vectorial local usando FAISS.

Requisitos:

- Crear índice FAISS para embeddings.
- Guardar el índice en disco.
- Cargar el índice automáticamente si ya existe.
- Permitir reconstrucción del índice si los documentos cambian.

7. Paralelizar procesamiento de documentos
Usar paralelización para:

- lectura de PDFs
- extracción de texto
- procesamiento de archivos

Se puede usar:
- ThreadPoolExecutor
o
- ProcessPoolExecutor

8. Mejorar manejo de memoria
Evitar:

- almacenar texto excesivo
- cargar archivos completos innecesariamente

Implementar:
- límites de tamaño
- limpieza de texto
- normalización.

9. Mejorar extracción de texto
Agregar:

- limpieza de caracteres extraños
- normalización de espacios
- eliminación de duplicados

10. Mejorar sistema de caché
El sistema actual usa JSON.

Mejorarlo para:

- evitar re-embeddings innecesarios
- validar hashes
- permitir invalidación automática del caché.

11. Preparar sistema para RAG avanzado
El sistema debe preparar el contexto para LLM de forma eficiente.

Implementar:

- ranking de resultados
- límite de tokens aproximado
- deduplicación de chunks
- contexto compacto.

12. Modularizar arquitectura
Separar el sistema en módulos:

document_loader.py
text_chunker.py
embedding_engine.py
vector_index.py
semantic_search.py
rag_context_builder.py

Esto mejora mantenibilidad.

13. Agregar logging
Reemplazar prints por logging:

- logging.info
- logging.warning
- logging.error

14. Manejo robusto de errores
Agregar manejo de excepciones consistente para:

- archivos corruptos
- PDFs dañados
- CSV inválidos
- errores de encoding.

Resultado esperado
------------------

El sistema mejorado debe:

- ser más rápido
- escalar a miles de documentos
- usar búsqueda vectorial eficiente
- tener arquitectura modular
- ser mantenible y extensible.

No eliminar funcionalidades existentes.
Solo mejorar la arquitectura, rendimiento y robustez.
