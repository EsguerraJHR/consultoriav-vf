import streamlit as st
from dotenv import load_dotenv
import os
import time
import re
# Importar el grafo completo en lugar de solo los componentes individuales
from graph.graph import app, set_debug
# Importar funciones específicas para consulta del libro
try:
    # Intentar importar primero
    from graph.chains.retrieval import query_ley_crecimiento
except ImportError:
    # Si no existe, importar las funciones necesarias y crear una versión local
    import sys
    from graph.chains.retrieval import query_pinecone
    
    # Definir constantes necesarias si no existen
    try:
        from graph.chains.retrieval import LEY_CRECIMIENTO_INDEX_NAME, LEY_CRECIMIENTO_NAMESPACE, LEY_CRECIMIENTO_TOP_K
    except ImportError:
        # Valores predeterminados basados en el análisis del código
        LEY_CRECIMIENTO_INDEX_NAME = "leycrecimiento"
        LEY_CRECIMIENTO_NAMESPACE = "leycrecimiento"
        LEY_CRECIMIENTO_TOP_K = 10
    
    # Crear una definición local de query_ley_crecimiento
    def query_ley_crecimiento(query, top_k=LEY_CRECIMIENTO_TOP_K):
        """
        Consulta específica para documentos del libro (definida localmente).
        """
        print("Usando definición local de query_ley_crecimiento")
        return query_pinecone(query, index_name=LEY_CRECIMIENTO_INDEX_NAME, namespace=LEY_CRECIMIENTO_NAMESPACE, top_k=top_k)

from graph.chains.reranking import retrieve_with_reranking
from graph.chains.openai_generation import generate_simple_response

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Ley 2010 de 2019",
    page_icon="📙",
    layout="wide"
)

# Título de la página
st.title("Libro: Análisis de la Ley de Crecimiento Económico - Ley 2010 de 2019")

# Descripción de la página
st.markdown("""
Esta sección le permite realizar consultas específicas sobre el libro **Análisis de la Ley de Crecimiento Económico - Ley 2010 de 2019**.

El asistente encontrará los pasajes más relevantes del libro y presentará una respuesta concisa.

Ideal para:
- Consultas sobre la Ley de Crecimiento Económico
- Entender los cambios introducidos por la Ley 2010 de 2019
- Análisis de impacto tributario de la ley de crecimiento
""")

# Verificar si Pinecone está configurado
try:
    import pinecone
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    index_name = "leycrecimiento"  # Índice específico para el libro
    
    if not pinecone_api_key:
        st.warning("No se ha configurado la API key de Pinecone. Por favor, configura la variable PINECONE_API_KEY en el archivo .env.")
    else:
        # Verificar que el índice existe
        pc = pinecone.Pinecone(api_key=pinecone_api_key)
        existing_indexes = [index.name for index in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            st.warning(f"El índice {index_name} no existe en Pinecone. Por favor, crea el índice primero.")
        else:
            # Inicializar estado de sesión para el libro
            if "ley_crecimiento_messages" not in st.session_state:
                st.session_state.ley_crecimiento_messages = []
            
            # Función para formatear el texto con citas numeradas
            def formatear_texto_con_citas(texto, citas):
                """
                Formatea el texto con citas numeradas en HTML.
                """
                if not citas:
                    return texto
                
                # Crear un diccionario de citas para acceder rápidamente a la información
                citas_dict = {}
                for i, cita in enumerate(citas):
                    citas_dict[i+1] = cita
                
                # Función para reemplazar cada cita con su versión HTML
                def reemplazar_cita(match):
                    num_cita = int(match.group(1))
                    return f'<sup>[{num_cita}]</sup>'
                
                texto_formateado = re.sub(r'\[(\d+)\]', reemplazar_cita, texto)
                
                return texto_formateado
            
            # Mostrar mensajes anteriores
            for message in st.session_state.ley_crecimiento_messages:
                with st.chat_message(message["role"]):
                    # Si hay citas, formatear el texto con ellas
                    if message["role"] == "assistant" and "citations" in message and message["citations"]:
                        formatted_content = formatear_texto_con_citas(message["content"], message["citations"])
                        st.markdown(formatted_content, unsafe_allow_html=True)
                    else:
                        st.markdown(message["content"])
                    
                    # Si hay citas, mostrarlas
                    if "citations" in message and message["citations"]:
                        with st.expander("Ver referencias"):
                            for i, citation in enumerate(message["citations"]):
                                # Eliminar las extensiones del título del documento
                                document_title = citation['document_title']
                                document_title = document_title.replace('.pdf', '').replace('.html', '')
                                st.markdown(f"**[{i+1}]** `{document_title}`")
                                st.markdown(f"*\"{citation['cited_text']}\"*")
                    
                    # Si hay documentos, mostrarlos
                    if "documents" in message:
                        with st.expander("Ver fuentes utilizadas"):
                            for i, doc in enumerate(message["documents"]):
                                source = doc.metadata.get('source', f'Documento {i+1}')
                                # Eliminar las extensiones del nombre de la fuente
                                source = source.replace('.pdf', '').replace('.html', '')
                                # Limpiar prefijos comunes de la fuente
                                prefixes_to_remove = [
                                    "pinecone_docs/", "Pinecone: ",
                                    f"pinecone_{index_name}/data/{index_name}/", f"data/{index_name}/",
                                    f"{index_name}/"
                                ]
                                for prefix in prefixes_to_remove:
                                    if prefix in source:
                                        source = source.replace(prefix, "")
                                # Aplicar expresión regular general para cualquier otro prefijo de tipo data/XXX/
                                source = re.sub(r'(?:^|/)data/\w+/', '', source)
                                # Mostrar la página si está disponible
                                page = doc.metadata.get('page', None)
                                page_info = f" (Pág. {page})" if page and page != 0 else ""
                                st.markdown(f"**Fuente {i+1}:** `{source}{page_info}`")
                                st.markdown(f"```\n{doc.page_content}\n```")
                    
                    # Si hay un flujo, mostrarlo
                    if "flow" in message:
                        with st.expander("Ver flujo de procesamiento"):
                            st.markdown(message["flow"])
            
            # Input para la consulta
            query = st.chat_input("Escribe tu consulta sobre la Ley de Crecimiento Económico...")
            
            # Procesar la consulta
            if query:
                # Agregar la consulta del usuario a los mensajes
                st.session_state.ley_crecimiento_messages.append({
                    "role": "user", 
                    "content": query
                })
                
                # Mostrar la consulta en la interfaz
                with st.chat_message("user"):
                    st.markdown(query)
                
                # Mostrar un spinner mientras se procesa la consulta
                with st.chat_message("assistant"):
                    # Crear un placeholder para mostrar el flujo en tiempo real
                    flow_placeholder = st.empty()
                    
                    # Usar una lista para almacenar los pasos del flujo
                    flow_steps = []
                    
                    # Función para actualizar el flujo
                    def update_flow(step):
                        flow_steps.append(f"- {step}")
                        flow_text = ""
                        for s in flow_steps:
                            flow_text += s + "\n"
                        flow_placeholder.markdown(f"**Procesando:**\n{flow_text}")
                    
                    # Mostrar el flujo de procesamiento
                    update_flow(f"🔄 Iniciando procesamiento de la consulta sobre la Ley de Crecimiento Económico...")
                    time.sleep(0.5)
                    
                    update_flow("🧠 Analizando la consulta...")
                    time.sleep(0.5)
                    
                    update_flow("🔍 Buscando en el libro Análisis de la Ley de Crecimiento Económico...")
                    time.sleep(1)
                    
                    # Consultar el índice del libro
                    try:
                        # Recuperar documentos con reranking
                        print("Ley_Crecimiento.py: Consultando el índice del libro")
                        documents = retrieve_with_reranking(query, query_ley_crecimiento, top_k=10)
                        print(f"Ley_Crecimiento.py: Recuperados {len(documents)} documentos después del reranking")
                        
                        # Verificar si se encontraron documentos
                        if not documents:
                            update_flow("❌ No se encontraron pasajes relevantes en el libro")
                            response = "Lo siento, no encontré información relevante sobre tu consulta en el libro Análisis de la Ley de Crecimiento Económico. Por favor, intenta reformular tu pregunta."
                            final_flow = '\n'.join(flow_steps)
                            flow_placeholder.empty()
                            st.markdown(response)
                            citations = []
                            documents = []
                        else:
                            update_flow(f"📝 Encontrados {len(documents)} pasajes relevantes del libro")
                            time.sleep(0.5)
                            
                            update_flow("✍️ Generando respuesta basada en el libro...")
                            time.sleep(0.5)
                            
                            # Para cada documento, añadir la metadata de source_index si no existe
                            for doc in documents:
                                if 'source_index' not in doc.metadata:
                                    doc.metadata['source_index'] = 'Ley Crecimiento'
                            
                            # Generar respuesta con OpenAI (formato simplificado)
                            openai_response = generate_simple_response(query, documents)
                            response = openai_response["text"]
                            citations = openai_response.get("citations", [])
                            
                            update_flow("🔎 Verificando que la respuesta sea relevante...")
                            time.sleep(0.5)
                            
                            if citations:
                                update_flow(f"📌 Añadiendo {len(citations)} citas a la respuesta...")
                                time.sleep(0.5)
                            
                            update_flow("✨ Respuesta generada con éxito!")
                            
                            # Guardar el flujo para mostrarlo en el historial
                            final_flow = '\n'.join(flow_steps)
                            
                            # Limpiar el placeholder
                            flow_placeholder.empty()
                            
                            # Procesar la respuesta
                            try:
                                # Verificar si hay citas en la respuesta
                                if "[1]" in response or response.find("\n\n### Citas\n\n") > -1:
                                    # Si hay citas, separarlas de la respuesta principal
                                    if "\n\n### Citas\n\n" in response:
                                        # Separar el texto principal de las citas
                                        main_response, citations_text = response.split("\n\n### Citas\n\n", 1)
                                        
                                        # Mostrar el texto principal
                                        st.write(main_response)
                                        
                                        # Mostrar las citas en un expander
                                        with st.expander("Referencias:", expanded=False):
                                            st.write(f"### Citas\n\n{citations_text}")
                                    else:
                                        # Si no hay formato específico, mostrar toda la respuesta
                                        st.write(response)
                                else:
                                    # Si no hay citas, mostrar la respuesta completa
                                    st.write(response)
                            except Exception as e:
                                print(f"Error al procesar la respuesta: {str(e)}")
                                import traceback
                                traceback.print_exc()
                                
                                error_message = f"Lo siento, ocurrió un error al procesar la respuesta: {str(e)}"
                                st.error(error_message)
                                
                                # Guardar el error en el historial
                                st.session_state.ley_crecimiento_messages.append({
                                    "role": "assistant",
                                    "content": error_message
                                })
                        
                        # Guardar el mensaje en el historial
                        st.session_state.ley_crecimiento_messages.append({
                            "role": "assistant",
                            "content": response,
                            "citations": citations if 'citations' in locals() else [],
                            "documents": documents if 'documents' in locals() else [],
                            "flow": final_flow if 'final_flow' in locals() else ""
                        })
                    
                    except Exception as e:
                        print(f"Error al procesar la consulta: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        
                        error_message = f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}"
                        st.error(error_message)
                        
                        # Guardar el error en el historial
                        st.session_state.ley_crecimiento_messages.append({
                            "role": "assistant",
                            "content": error_message
                        })

except Exception as e:
    st.error(f"Error general: {str(e)}")
    import traceback
    traceback.print_exc() 