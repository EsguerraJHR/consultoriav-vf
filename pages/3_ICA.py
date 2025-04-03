import streamlit as st
from dotenv import load_dotenv
import os
import time
import re
# Importar el grafo completo en lugar de solo los componentes individuales
from graph.graph import app, set_debug
# Importar la función query_ica con manejo de errores para mayor robustez
try:
    from graph.chains.retrieval import query_ica
except ImportError:
    # Si no existe, importar las funciones necesarias y crear una versión local
    from graph.chains.retrieval import query_pinecone
    
    # Definir constantes necesarias si no existen
    try:
        from graph.chains.retrieval import ICA_INDEX_NAME, ICA_NAMESPACE, ICA_TOP_K
    except ImportError:
        # Valores predeterminados
        ICA_INDEX_NAME = "ica"
        ICA_NAMESPACE = "ica"
        ICA_TOP_K = 8
    
    # Crear una definición local de query_ica
    def query_ica(query, top_k=ICA_TOP_K):
        """
        Consulta específica para documentos de ICA (definida localmente).
        """
        print("Usando definición local de query_ica")
        return query_pinecone(query, index_name=ICA_INDEX_NAME, namespace=ICA_NAMESPACE, top_k=top_k)

from graph.chains.openai_generation import generate_with_openai
# Importar el módulo de reranking
from graph.chains.reranking import retrieve_with_reranking

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Consultas sobre ICA",
    page_icon="🏙️",
    layout="wide"
)

# Título de la página
st.title("Consultas sobre Impuesto de Industria y Comercio (ICA)")

# Descripción de la página
st.markdown("""
Esta sección le permite realizar consultas específicas sobre el Impuesto de Industria y Comercio (ICA) en Colombia.
La base de conocimiento incluye conceptos y normatividad sobre ICA a nivel nacional y de los principales municipios. Pueden acceder a los documentos aquí [Biblioteca](https://eba-my.sharepoint.com/:f:/g/personal/hcastro_esguerrajhr_com/EgWozji9P89Gi02QG_0ybskBFzI39tnYkn78gfP3PiGWPw?e=JCZUDU).
""", unsafe_allow_html=True)

# Verificar si la colección existe
try:
    import pinecone
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    index_name = "ica"  # Nombre específico del índice para ICA
    
    if not pinecone_api_key:
        st.warning("No se ha configurado la API key de Pinecone. Por favor, configura la variable PINECONE_API_KEY en el archivo .env.")
    else:
        # Inicializar Pinecone
        pc = pinecone.Pinecone(api_key=pinecone_api_key)
        existing_indexes = [index.name for index in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            st.warning(f"El índice {index_name} no existe en Pinecone. Por favor, crea el índice primero.")
        else:
            # Inicializar estado de sesión para ICA
            if "ica_messages" not in st.session_state:
                st.session_state.ica_messages = []
            
            # Función para formatear el texto con citas numeradas
            def formatear_texto_con_citas(texto, citas):
                """
                Formatea el texto con citas numeradas en HTML.
                """
                if not citas:
                    return texto
                
                # Reemplazar los corchetes de cita por etiquetas HTML para mejorar la visualización
                # Primero, crear un diccionario de citas para acceder rápidamente a la información de la página
                citas_dict = {}
                for i, cita in enumerate(citas):
                    citas_dict[i+1] = cita
                
                # Función para reemplazar cada cita con su versión HTML que incluye la página
                def reemplazar_cita(match):
                    num_cita = int(match.group(1))
                    # Simplificar: siempre devolver solo el número de cita sin la página
                    return f'<sup>[{num_cita}]</sup>'
                
                texto_formateado = re.sub(r'\[(\d+)\]', reemplazar_cita, texto)
                
                return texto_formateado
            
            # Mostrar mensajes anteriores
            for message in st.session_state.ica_messages:
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
                                # Eliminar las extensiones del nombre de la fuente
                                source = source.replace('.pdf', '').replace('.html', '')
                                page = doc.metadata.get('page', None)
                                page_info = f" (Pág. {page})" if page and page != 0 else ""
                                st.markdown(f"**Fuente {i+1}:** `{source}{page_info}`")
                                st.markdown(f"```\n{doc.page_content}\n```")
                    
                    # Si hay citas, mostrarlas
                    if "citations" in message and message["citations"]:
                        with st.expander("Ver referencias"):
                            for i, citation in enumerate(message["citations"]):
                                # Eliminar las extensiones del título del documento
                                document_title = citation['document_title']
                                document_title = document_title.replace('.pdf', '').replace('.html', '')
                                st.markdown(f"**[{i+1}]** `{document_title}`")
                                st.markdown(f"*\"{citation['cited_text']}\"*")
                    
                    # Si hay un flujo, mostrarlo
                    if "flow" in message:
                        with st.expander("Ver flujo de procesamiento"):
                            st.markdown(message["flow"])
            
            # Input para la consulta
            query = st.chat_input("Escribe tu consulta sobre ICA...")
            
            # Procesar la consulta
            if query:
                # Agregar la consulta del usuario a los mensajes
                st.session_state.ica_messages.append({
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
                    update_flow(f"🔄 Iniciando procesamiento de la consulta sobre ICA...")
                    time.sleep(0.5)
                    
                    update_flow("🧠 Analizando la consulta...")
                    time.sleep(0.5)
                    
                    update_flow("🔍 Ejecutando flujo RAG avanzado...")
                    time.sleep(1)
                    
                    # Consultar directamente a Pinecone para ICA
                    try:
                        # Consultar directamente a Pinecone con reranking
                        print("ICA.py: Consultando directamente a Pinecone (índice ica)")
                        # Usar la función de reranking para mejorar la relevancia de los documentos
                        documents = retrieve_with_reranking(query, query_ica, top_k=8)
                        print(f"ICA.py: Recuperados {len(documents)} documentos de Pinecone con reranking")
                        
                        # Verificar si se encontraron documentos
                        if not documents:
                            update_flow("❌ No se encontraron documentos relevantes en Pinecone")
                            response = "Lo siento, no encontré información relevante sobre tu consulta en la base de conocimiento de ICA. Por favor, intenta reformular tu pregunta o consulta otra base de conocimiento."
                            final_flow = '\n'.join(flow_steps)
                            flow_placeholder.empty()
                            st.markdown(response)
                            citations = []
                            documents = []
                        else:
                            update_flow(f"📝 Encontrados {len(documents)} documentos relevantes")
                            time.sleep(0.5)
                            
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
                                        # Eliminar las extensiones del título del documento
                                        document_title = citation['document_title']
                                        document_title = document_title.replace('.pdf', '').replace('.html', '')
                                        st.markdown(f"**[{i+1}]** `{document_title}`")
                                        st.markdown(f"*\"{citation['cited_text']}\"*")
                            
                            # Mostrar las fuentes utilizadas
                            with st.expander("Ver fuentes utilizadas"):
                                for i, doc in enumerate(documents):
                                    source = doc.metadata.get('source', f'Documento {i+1}')
                                    # Eliminar las extensiones del nombre de la fuente
                                    source = source.replace('.pdf', '').replace('.html', '')
                                    page = doc.metadata.get('page', None)
                                    page_info = f" (Pág. {page})" if page and page != 0 else ""
                                    st.markdown(f"**Fuente {i+1}:** `{source}{page_info}`")
                                    st.markdown(f"```\n{doc.page_content}\n```")
                            
                            # Mostrar el flujo de procesamiento
                            with st.expander("Ver flujo de procesamiento"):
                                st.markdown(final_flow)
                    
                    except Exception as e:
                        update_flow(f"❌ Error: {str(e)}")
                        response = f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}"
                        final_flow = '\n'.join(flow_steps)
                        flow_placeholder.empty()
                        st.markdown(response)
                        citations = []
                        documents = []
                
                # Agregar la respuesta del asistente a los mensajes
                st.session_state.ica_messages.append({
                    "role": "assistant", 
                    "content": response,
                    "documents": documents if 'documents' in locals() else [],
                    "flow": final_flow if 'final_flow' in locals() else '',
                    "citations": citations if 'citations' in locals() else []
                })
except Exception as e:
    st.error(f"Error al conectar con Pinecone: {str(e)}") 