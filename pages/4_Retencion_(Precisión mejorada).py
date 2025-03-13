import streamlit as st
from dotenv import load_dotenv
import os
import time
import re
# Importar el grafo completo en lugar de solo los componentes individuales
from graph.graph import app, set_debug
from graph.chains.retrieval import query_retencion
from graph.chains.openai_generation import generate_with_openai
# Importar el módulo de reranking
from graph.chains.reranking import retrieve_with_reranking

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Consultas sobre Retención",
    page_icon="💸",
    layout="wide"
)

# Título de la página
st.title("Consultas sobre Retención en la Fuente")

# Descripción de la página
st.markdown("""
Esta sección le permite realizar consultas específicas sobre Retención en la Fuente en Colombia.
La base de conocimiento incluye conceptos de la Dian sobre retención desde enero de 2017 hasta diciembre de 2024. Contiene 200 conceptos de la Dian sobre retención. Pueden acceder a los documentos aquí [Biblioteca](https://eba-my.sharepoint.com/:f:/g/personal/hcastro_esguerrajhr_com/EgWozji9P89Gi02QG_0ybskBFzI39tnYkn78gfP3PiGWPw?e=JCZUDU).
""")

# Verificar si la colección existe
try:
    import pinecone
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    index_name = "retencion"  # Nombre específico del índice para Retención
    
    if not pinecone_api_key:
        st.warning("No se ha configurado la API key de Pinecone. Por favor, configura la variable PINECONE_API_KEY en el archivo .env.")
    else:
        # Inicializar Pinecone
        pc = pinecone.Pinecone(api_key=pinecone_api_key)
        existing_indexes = [index.name for index in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            st.warning(f"El índice {index_name} no existe en Pinecone. Por favor, crea el índice primero.")
        else:
            # Inicializar estado de sesión para Retención
            if "retencion_messages" not in st.session_state:
                st.session_state.retencion_messages = []
            
            # Función para formatear el texto con citas numeradas
            def formatear_texto_con_citas(texto, citas):
                """
                Formatea el texto con citas numeradas en HTML.
                """
                if not citas:
                    return texto
                
                # Reemplazar los corchetes de cita por etiquetas HTML para mejorar la visualización
                texto_formateado = re.sub(r'\[(\d+)\]', r'<sup>[\1]</sup>', texto)
                
                return texto_formateado
            
            # Mostrar mensajes anteriores
            for message in st.session_state.retencion_messages:
                with st.chat_message(message["role"]):
                    # Si hay citas, formatear el texto con ellas
                    if message["role"] == "assistant" and "citations" in message and message["citations"]:
                        formatted_content = formatear_texto_con_citas(message["content"], message["citations"])
                        st.markdown(formatted_content, unsafe_allow_html=True)
                    else:
                        st.markdown(message["content"])
                    
                    # Si hay documentos, mostrarlos
                    if "documents" in message:
                        with st.expander("Ver fuentes utilizadas"):
                            for i, doc in enumerate(message["documents"]):
                                source = doc.metadata.get('source', f'Documento {i+1}')
                                st.markdown(f"**Fuente {i+1}:** `{source}`")
                                st.markdown(f"```\n{doc.page_content}\n```")
                    
                    # Si hay citas, mostrarlas
                    if "citations" in message and message["citations"]:
                        with st.expander("Ver referencias"):
                            for i, citation in enumerate(message["citations"]):
                                st.markdown(f"**[{i+1}]** `{citation['document_title']}`")
                                st.markdown(f"*\"{citation['cited_text']}\"*")
                    
                    # Si hay un flujo, mostrarlo
                    if "flow" in message:
                        with st.expander("Ver flujo de procesamiento"):
                            st.markdown(message["flow"])
            
            # Input para la consulta
            query = st.chat_input("Escribe tu consulta sobre Retención en la Fuente...")
            
            # Procesar la consulta
            if query:
                # Agregar la consulta del usuario a los mensajes
                st.session_state.retencion_messages.append({
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
                    
                    # Usar una lista para almacenar los pasos del flujo (evita problemas con nonlocal)
                    flow_steps = []
                    
                    # Función para actualizar el flujo
                    def update_flow(step):
                        flow_steps.append(f"- {step}")
                        flow_text = ""
                        for s in flow_steps:
                            flow_text += s + "\n"
                        flow_placeholder.markdown(f"**Procesando:**\n{flow_text}")
                    
                    # Mostrar el flujo de procesamiento
                    update_flow(f"🔄 Iniciando procesamiento de la consulta sobre Retención...")
                    time.sleep(0.5)
                    
                    update_flow("🧠 Analizando la consulta...")
                    time.sleep(0.5)
                    
                    update_flow("🔍 Ejecutando flujo RAG avanzado...")
                    time.sleep(1)
                    
                    # Consultar directamente a Pinecone para Retención
                    try:
                        # Consultar directamente a Pinecone con reranking
                        print("Retencion.py: Consultando directamente a Pinecone (índice retencion)")
                        # Usar la función de reranking para mejorar la relevancia de los documentos
                        documents = retrieve_with_reranking(query, query_retencion, top_k=8)
                        print(f"Retencion.py: Recuperados {len(documents)} documentos de Pinecone con reranking")
                        
                        # Verificar si se encontraron documentos
                        if not documents:
                            update_flow("❌ No se encontraron documentos relevantes en Pinecone")
                            response = "Lo siento, no encontré información relevante sobre tu consulta en la base de conocimiento de Retención. Por favor, intenta reformular tu pregunta o consulta otra base de conocimiento."
                            final_flow = '\n'.join(flow_steps)
                            flow_placeholder.empty()
                            st.markdown(response)
                            citations = []
                            documents = []
                        else:
                            update_flow(f"📝 Encontrados {len(documents)} documentos relevantes")
                            update_flow("🔄 Aplicado reranking para mejorar la relevancia")
                            time.sleep(0.5)
                            
                            update_flow("✍️ Generando respuesta...")
                            time.sleep(0.5)
                            
                            # Generar respuesta con OpenAI
                            openai_response = generate_with_openai(query, documents)
                            response = openai_response["text"]
                            citations = openai_response.get("citations", [])
                            
                            update_flow("🔎 Verificando que no haya alucinaciones...")
                            time.sleep(0.5)
                            
                            update_flow("✅ Verificando que la respuesta aborde la consulta...")
                            time.sleep(0.5)
                            
                            if citations:
                                update_flow(f"📌 Añadiendo {len(citations)} citas a la respuesta...")
                                time.sleep(0.5)
                            
                            update_flow("✨ Respuesta generada con éxito!")
                            
                            # Guardar el flujo para mostrarlo en el historial
                            final_flow = '\n'.join(flow_steps)
                            
                            # Limpiar el placeholder
                            flow_placeholder.empty()
                            
                            # Formatear la respuesta con citas si existen
                            if citations:
                                formatted_response = formatear_texto_con_citas(response, citations)
                                st.markdown(formatted_response, unsafe_allow_html=True)
                            else:
                                st.markdown(response)
                            
                            # Mostrar las citas si existen
                            if citations:
                                with st.expander("Ver referencias"):
                                    for i, citation in enumerate(citations):
                                        st.markdown(f"**[{i+1}]** `{citation['document_title']}`")
                                        st.markdown(f"*\"{citation['cited_text']}\"*")
                            
                            # Mostrar las fuentes utilizadas
                            with st.expander("Ver fuentes utilizadas"):
                                for i, doc in enumerate(documents):
                                    source = doc.metadata.get('source', f'Documento {i+1}')
                                    st.markdown(f"**Fuente {i+1}:** `{source}`")
                                    st.markdown(f"```\n{doc.page_content}\n```")
                            
                            # Mostrar el flujo de procesamiento
                            with st.expander("Ver flujo de procesamiento"):
                                st.markdown(final_flow)
                    
                    except Exception as e:
                        update_flow(f"❌ Error al consultar Pinecone o generar respuesta: {str(e)}")
                        response = f"Lo siento, ocurrió un error: {str(e)}"
                        final_flow = '\n'.join(flow_steps)
                        flow_placeholder.empty()
                        st.markdown(response)
                        citations = []
                        documents = []
                
                # Agregar la respuesta del asistente a los mensajes
                st.session_state.retencion_messages.append({
                    "role": "assistant", 
                    "content": response,
                    "documents": documents if 'documents' in locals() else [],
                    "flow": final_flow if 'final_flow' in locals() else '',
                    "citations": citations if 'citations' in locals() else []
                })
except Exception as e:
    st.error(f"Error al conectar con Pinecone: {str(e)}")

# Información adicional en el sidebar
with st.sidebar:
    st.header("Información sobre Retención")
    
    # Botón para limpiar la conversación
    if "retencion_messages" in st.session_state:
        if st.button("Limpiar conversación", use_container_width=True):
            st.session_state.retencion_messages = []
            st.rerun() 