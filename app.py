"""
IA Local Vargas - Asistente Personal con IA
================================================
Sistema de IA local con:
- Memoria persistente categorizada (corto/largo plazo)
- Sistema RAG para documentos con busqueda semantica
- Busqueda web
- Ejecucion de codigo segura
- Streaming de respuestas
- Limpieza automatica de memorias
Compatible con Gradio 6+
"""

import os
import sys
import socket
import json
import gradio as gr
from datetime import datetime
import ollama

# Imports de modulos propios - Memory Engine
from memory_engine import (
    init_db,
    save_memory,
    search_memory_string as search_memory,
    get_memory_count,
    clear_memory,
    get_memory_stats,
    clean_old_memories,
    get_important_memories,
    get_long_term_memories,
    get_short_term_memories,
    get_memory,
    get_all_memories,
    add_relation,
    get_related_memories,
    classify_memory,
    embed
)
from documents import (
    read_documents, get_document_info, rebuild_cache, 
    get_relevant_documents, build_document_embeddings
)
from web_search import search_web
from code_agent import run_python
from plugins import process_plugin, plugin_manager

# ============================================
# CONFIGURACION
# ============================================

MODEL = os.getenv("OLLAMA_MODEL", "llama3")
MAX_DOCUMENT_CHARS = 15000
MAX_WEB_RESULTS = 3
MAX_MEMORY_RESULTS = 5

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048

conversation_history = []
documents_text = ""


def find_free_port(start_port=7860, max_attempts=20):
    """Encuentra un puerto disponible"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('', port))
                print(f"Puerto encontrado: {port}")
                return port
        except OSError:
            print(f"  - Puerto {port} en uso, intentando siguiente...")
            continue
    return start_port + max_attempts - 1


def initialize_system():
    """Inicializa el sistema con limpieza automatica"""
    print("Initiating IA Local Vargas...")
    try:
        clean_old_memories()
    except Exception as e:
        print(f"Warning en limpieza: {e}")
    
    try:
        stats = get_memory_stats()
        print(f"Memoria: {stats.get('total', 0)} entradas")
    except Exception as e:
        print(f"Warning obteniendo stats: {e}")


def load_documents():
    """Carga los documentos al iniciar"""
    global documents_text
    try:
        print("Cargando documentos...")
        documents_text = read_documents(use_cache=True)
        
        print("Generando embeddings de documentos...")
        build_document_embeddings()
        
        doc_info = get_document_info()
        print(f"{len(doc_info)} documento(s) cargado(s)")
        return True
    except Exception as e:
        print(f"Warning cargando documentos: {e}")
        documents_text = ""
        return False


def build_prompt(user_message: str, use_rag: bool = True) -> str:
    """Construye el prompt completo para el modelo"""
    # 1. Buscar memoria relevante
    try:
        memory_context = search_memory(user_message, n_results=MAX_MEMORY_RESULTS)
    except Exception as e:
        print(f"Warning buscando memoria: {e}")
        memory_context = ""
    
    # 2. Buscar documentos relevantes
    doc_context = ""
    if use_rag:
        try:
            doc_context = get_relevant_documents(user_message, max_chars=5000, n_results=3)
        except Exception as e:
            print(f"Warning en RAG: {e}")
        
        if not doc_context:
            keywords = ["documento", "pdf", "python", "curso", "leccion", "materia", "tarea"]
            if any(kw in user_message.lower() for kw in keywords):
                doc_context = documents_text[:MAX_DOCUMENT_CHARS]
                if len(documents_text) > MAX_DOCUMENT_CHARS:
                    doc_context += f"\n\n[... y {len(documents_text) - MAX_DOCUMENT_CHARS} caracteres mas]"
    
    # 3. Busqueda web
    web_context = ""
    keywords_web = ["actual", "noticia", "2024", "2025", "reciente", "hoy", "hoy en dia"]
    if any(kw in user_message.lower() for kw in keywords_web):
        try:
            web_context = search_web(user_message)
        except Exception as e:
            print(f"Warning en busqueda web: {e}")
    
    # 4. Detectar si necesita ejecutar codigo
    needs_code = any(kw in user_message.lower() for kw in [
        "ejecuta", "calcula", "codigo", "python", "programa", "script"
    ])
    
    # Construir prompt
    prompt_parts = []
    
    if memory_context:
        prompt_parts.append(f"CONVERSACION ANTERIOR:\n{memory_context}")
    
    if doc_context:
        prompt_parts.append(f"DOCUMENTOS RELEVANTES:\n{doc_context}")
    
    if web_context:
        prompt_parts.append(f"INFORMACION ACTUAL:\n{web_context}")
    
    prompt_parts.append(f"PREGUNTA ACTUAL:\n{user_message}")
    
    if needs_code:
        prompt_parts.append("""
INSTRUCCION ESPECIAL: 
El usuario quiere ejecutar codigo Python. Responde SOLO con el codigo apropiado 
envuelto en bloques markdown ```python ... ``` y luego ejecutalo si es necesario.
""")
    
    system_prompt = """Eres un asistente de IA util y amigable. 
- Responde de manera clara y concisa
- Si tienes informacion de documentos, usala para responder
- Si no sabes algo, dilo honestamente
- Usa espanol naturalmente"""
    
    return f"{system_prompt}\n\n" + "\n\n".join(prompt_parts)


def chat_with_ai(message: str, history: list, temperature: float, max_tokens: int):
    """Funcion principal de chat con streaming"""
    global conversation_history
    
    # Gradio 6+ espera formato de diccionarios {"role": "...", "content": "..."}
    if history is None:
        history = []
    
    if not message.strip():
        return history
    
    try:
        prompt = build_prompt(message)
        
        # Validar que prompt sea string
        if not isinstance(prompt, str):
            prompt = str(prompt) if prompt else " "
        
        # Guardar mensaje del usuario en memoria
        try:
            save_memory(f"Usuario: {message}", importance=3)
        except Exception as e:
            print(f"Warning guardando memoria: {e}")
        
        # Verificar si es comando de plugin
        plugin_result = process_plugin(message)
        if plugin_result:
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": plugin_result})
            return history
        
        # Verificar si es comando de codigo
        if message.lower().startswith("ejecuta:"):
            code = message[8:].strip()
            result = run_python(code)
            full_response = f"Codigo ejecutado:\n\n{code}\n\n{result}"
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_response})
            return history
        
        # Verificar si es comando de busqueda web
        if message.lower().startswith("busca:"):
            query = message[6:].strip()
            try:
                web_results = search_web(query)
                full_response = f"Resultados de busqueda para: {query}\n\n{web_results}"
            except Exception as e:
                full_response = f"Warning en busqueda: {str(e)}"
            
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_response})
            return history
        
        # Obtener respuesta con streaming
        print(f"Procesando con {MODEL}...")
        
        # Agregar mensaje del usuario al historial
        history.append({"role": "user", "content": message})
        
        # Formato de mensajes para Ollama
        messages = [{"role": "user", "content": prompt}]
        
        stream = ollama.chat(
            model=MODEL,
            messages=messages,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )
        
        full_response = ""
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                full_response += content
                # Yield history con respuesta parcial
                yield history + [{"role": "assistant", "content": full_response}]
        
        # Guardar respuesta en memoria
        try:
            save_memory(f"Asistente: {full_response}", importance=3)
        except:
            pass
        
        conversation_history.append({
            "user": message,
            "assistant": full_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Retornar history final
        yield history + [{"role": "assistant", "content": full_response}]
        
    except Exception as e:
        error_msg = f"Warning: {str(e)}"
        print(f"Error en chat: {e}")
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        yield history


def clear_chat():
    """Limpia el historial de chat"""
    global conversation_history
    conversation_history = []
    return [], ""


def export_conversation(history: list) -> str:
    """Exporta la conversacion a texto"""
    if not history:
        return "No hay conversacion para exportar"
    
    text = "# Conversacion con IA Local Vargas\n\n"
    text += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for msg in history:
        # Formato puede ser dict o tupla
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
        elif isinstance(msg, (list, tuple)) and len(msg) >= 2:
            role, content = msg[0], msg[1]
        else:
            role = "user"
            content = str(msg)
        
        if role == "user" or role == "Usuario":
            text += f"**Usuario:** {content}\n\n"
        else:
            text += f"**Asistente:** {content}\n\n"
        text += "---\n\n"
    
    return text


def get_ollama_models():
    """Obtiene la lista de modelos disponibles en Ollama"""
    try:
        response = ollama.list()
        # Nueva API: response.models es una lista
        if hasattr(response, 'models'):
            return [m.model for m in response.models]
        # Formato antiguo
        elif isinstance(response, dict) and 'models' in response:
            return [m.get('name', 'unknown') for m in response.get('models', [])]
        return []
    except Exception as e:
        print(f"Warning listando modelos Ollama: {e}")
        return []


def get_status() -> str:
    """Retorna el estado del sistema"""
    try:
        doc_count = len(get_document_info())
        memory_count = get_memory_count()
        memory_stats = get_memory_stats()
        
        try:
            important = get_important_memories(min_importance=4, limit=5)
        except:
            important = []
        
        # Obtener modelos de Ollama
        model_names = get_ollama_models()
        
        cat_info = ""
        if "by_category" in memory_stats:
            for cat, count in memory_stats["by_category"].items():
                cat_info += f"- {cat}: {count}\n"
        
        scope_info = ""
        if "by_scope" in memory_stats:
            for scope, count in memory_stats["by_scope"].items():
                scope_name = "Largo plazo" if scope == "long" else "Corto plazo"
                scope_info += f"- {scope_name}: {count}\n"
        
        status = f"""
**Estado del Sistema**

| Componente | Estado |
|------------|--------|
| Modelo | {MODEL} |
| Documentos | {doc_count} archivos |
| Memoria | {memory_count} entradas |

**Categorias:**
{cat_info if cat_info else "Sin datos"}

**Scope de Memoria:**
{scope_info if scope_info else "Sin datos"}

**Memorias Importantes:** {len(important)}

**Modelos Ollama:** {', '.join(model_names) if model_names else 'No disponibles'}

Comandos:
- `ejecuta:` codigo Python (seguro)
- `busca:` busqueda web

Parametros: Temperature, Max Tokens
"""
        return status
    except Exception as e:
        return f"Warning: {e}"


def create_interface():
    """Crea la interfaz de Gradio - Compatible con Gradio 6+"""
    
    with gr.Blocks(title="IA Local Vargas") as demo:
        
        gr.Markdown("""
        # IA Local Vargas - Asistente Personal
        *Tu asistente de IA funcionando completamente en local*
        
        ### Caracteristicas:
        - Memoria persistente (corto/largo plazo)
        - Busqueda semantica en documentos
        - Ejecucion de codigo segura
        - Busqueda web
        - Streaming de respuestas
        """)
        
        with gr.Row():
            # Columna principal - Chat
            with gr.Column(scale=3):
                # Gradio 6+ espera formato de diccionarios
                chatbot = gr.Chatbot(
                    label="Conversacion",
                    height=500
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Escribe tu mensaje...", 
                        show_label=False, 
                        scale=4,
                        lines=3
                    )
                    send_btn = gr.Button("Enviar", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("Limpiar")
                    export_btn = gr.Button("Exportar")
                    status_btn = gr.Button("Estado")
                
                # Parametros del modelo
                with gr.Row():
                    temperature = gr.Slider(
                        minimum=0.0, maximum=1.0, 
                        value=DEFAULT_TEMPERATURE, 
                        step=0.1, 
                        label="Temperature",
                        info="0=preciso, 1=creativo"
                    )
                    max_tokens = gr.Slider(
                        minimum=256, maximum=4096, 
                        value=DEFAULT_MAX_TOKENS, 
                        step=256, 
                        label="Max Tokens"
                    )
            
            # Columna lateral - Info
            with gr.Column(scale=1):
                gr.Markdown("### Informacion")
                status_output = gr.Markdown(get_status())
                refresh_btn = gr.Button("Actualizar")
                
                gr.Markdown("""
                ### Comandos
                - **Chat**: Escribe tu pregunta
                - **Codigo**: `ejecuta: print("Hola")`
                - **Web**: `busca: noticias IA`
                
                ### Plugins
                - **Calculadora**: `calc: 2+2*3`
                - **Notas**: `nota: titulo: contenido`
                - **Tareas**: `tarea: + nueva tarea`
                - **Fecha/Hora**: `hora` o `fecha`
                - **Ayuda**: `ayuda` o `comandos`
                
                ### Memoria
                Las memorias importantes se guardan a largo plazo.
                """)
        
        # Event handlers
        send_btn.click(
            chat_with_ai, 
            [msg, chatbot, temperature, max_tokens], 
            chatbot
        )
        msg.submit(
            chat_with_ai, 
            [msg, chatbot, temperature, max_tokens], 
            chatbot
        )
        clear_btn.click(clear_chat, outputs=[chatbot, msg])
        export_btn.click(export_conversation, chatbot, status_output)
        status_btn.click(lambda: get_status(), outputs=status_output)
        refresh_btn.click(lambda: get_status(), outputs=status_output)
        
        # Cargar documentos al iniciar la interfaz
        try:
            load_documents()
        except Exception as e:
            print(f"Warning cargando documentos: {e}")
    
    return demo


if __name__ == "__main__":
    PORT = find_free_port()
    
    # Inicializar sistema
    initialize_system()
    
    print(get_status())
    
    print(f"\nIniciando interfaz web en puerto {PORT}...")
    demo = create_interface()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        share=False,
        show_error=True
    )

