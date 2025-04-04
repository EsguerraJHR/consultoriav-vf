import streamlit as st
from dotenv import load_dotenv
import os
import time
import re
# Importar el grafo completo en lugar de solo los componentes individuales
from graph.graph import app, set_debug
# Importar funciones específicas para consulta general
from graph.chains.reranking import retrieve_with_multi_index_reranking
from graph.chains.openai_generation import generate_simple_response

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Consulta General",
    page_icon="🔍",
    layout="wide"
)

# Título de la página
st.title("Consulta General en Todos los Índices")

# Descripción de la página
st.markdown("""
Esta sección le permite realizar consultas generales que buscan en **todos los índices** disponibles.

El asistente encontrará la información más relevante independientemente de su origen (Renta, IVA, Retención, Timbre, ICA, etc.) 
y presentará una respuesta concisa sin la estructura formal de las otras secciones.

Ideal para:
- Consultas que pueden abarcar múltiples impuestos
- Búsquedas exploratorias cuando no está seguro del área específica
- Obtener respuestas rápidas y directas
""")

# Verificar si Pinecone está configurado
try:
    import pinecone
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    
    if not pinecone_api_key:
        st.warning("No se ha configurado la API key de Pinecone. Por favor, configura la variable PINECONE_API_KEY en el archivo .env.")
    else:
        # Inicializar estado de sesión para consultas generales
        if "general_messages" not in st.session_state:
            st.session_state.general_messages = []
        
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
        for message in st.session_state.general_messages:
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
                            # Limpiar prefijos comunes de la fuente
                            prefixes_to_remove = [
                                "pinecone_docs/", "Pinecone: ",
                                "pinecone_timbre/data/timbre/", "pinecone_renta/data/renta/",
                                "pinecone_iva/data/iva/", "pinecone_retencion/data/retencion/",
                                "pinecone_ipoconsumo/data/ipoconsumo/", "pinecone_aduanas/data/aduanas/",
                                "pinecone_cambiario/data/cambiario/", "pinecone_ica/data/ica/",
                                "data/timbre/", "data/renta/", "data/iva/", "data/ica/",
                                "data/retencion/", "data/ipoconsumo/", "data/aduanas/", "data/cambiario/"
                            ]
                            for prefix in prefixes_to_remove:
                                if prefix in source:
                                    source = source.replace(prefix, "")
                            # Aplicar expresión regular general para cualquier otro prefijo de tipo data/XXX/
                            source = re.sub(r'(?:^|/)data/\w+/', '', source)
                            # Mostrar el índice de origen si está disponible
                            index_name = doc.metadata.get('source_index', '')
                            index_info = f" [{index_name}]" if index_name else ""
                            page = doc.metadata.get('page', None)
                            page_info = f" (Pág. {page})" if page and page != 0 else ""
                            st.markdown(f"**Fuente {i+1}:** `{source}{index_info}{page_info}`")
                            st.markdown(f"```\n{doc.page_content}\n```")
                
                # Si hay citas, mostrarlas
                if "citations" in message and message["citations"]:
                    with st.expander("Ver referencias"):
                        for i, citation in enumerate(message["citations"]):
                            # Eliminar las extensiones del título del documento
                            document_title = citation['document_title']
                            document_title = document_title.replace('.pdf', '').replace('.html', '')
                            # Mostrar el documento con su índice de origen
                            index_name = ""
                            if "source_index" in citation:
                                index_name = f" [{citation['source_index']}]"
                            st.markdown(f"**[{i+1}]** `{document_title}{index_name}`")
                            st.markdown(f"*\"{citation['cited_text']}\"*")
                
                # Si hay información de índices utilizados, mostrarla
                if "indices_used" in message and message["indices_used"]:
                    with st.expander("Índices consultados"):
                        st.markdown("##### Índices de donde proviene la información:")
                        for index in message["indices_used"]:
                            st.markdown(f"- {index}")
                
                # Si hay un flujo, mostrarlo
                if "flow" in message:
                    with st.expander("Ver flujo de procesamiento"):
                        st.markdown(message["flow"])
        
        # Input para la consulta
        query = st.chat_input("Escribe tu consulta general...")
        
        # Procesar la consulta
        if query:
            # Agregar la consulta del usuario a los mensajes
            st.session_state.general_messages.append({
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
                update_flow(f"🔄 Iniciando procesamiento de la consulta general...")
                time.sleep(0.5)
                
                update_flow("🧠 Analizando la consulta...")
                time.sleep(0.5)
                
                update_flow("🔍 Buscando en todos los índices disponibles...")
                time.sleep(1)
                
                # Consultar todos los índices
                try:
                    # Recuperar documentos de múltiples índices con reranking
                    print("General.py: Consultando múltiples índices")
                    documents = retrieve_with_multi_index_reranking(query, top_k=12)
                    print(f"General.py: Recuperados {len(documents)} documentos después del reranking")
                    
                    # Verificar si se encontraron documentos
                    if not documents:
                        update_flow("❌ No se encontraron documentos relevantes en ningún índice")
                        response = "Lo siento, no encontré información relevante sobre tu consulta en ninguna de nuestras bases de conocimiento. Por favor, intenta reformular tu pregunta."
                        final_flow = '\n'.join(flow_steps)
                        flow_placeholder.empty()
                        st.markdown(response)
                        citations = []
                        documents = []
                        indices_used = []
                    else:
                        # Contar documentos por índice
                        indices_counts = {}
                        for doc in documents:
                            index_name = doc.metadata.get('source_index', 'Desconocido')
                            if index_name in indices_counts:
                                indices_counts[index_name] += 1
                            else:
                                indices_counts[index_name] = 1
                        
                        indices_str = ", ".join([f"{name} ({count})" for name, count in indices_counts.items()])
                        update_flow(f"📝 Encontrados {len(documents)} documentos relevantes en: {indices_str}")
                        time.sleep(0.5)
                        
                        update_flow("✍️ Generando respuesta basada en múltiples fuentes...")
                        time.sleep(0.5)
                        
                        # Generar respuesta con OpenAI (formato simplificado)
                        openai_response = generate_simple_response(query, documents)
                        response = openai_response["text"]
                        citations = openai_response.get("citations", [])
                        indices_used = openai_response.get("indices_used", [])
                        
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
                        
                        # Formatear la respuesta con citas si existen
                        if citations:
                            # Intentar formatear la respuesta, con manejo de errores
                            try:
                                formatted_response = formatear_texto_con_citas(response, citations)
                                st.markdown(formatted_response, unsafe_allow_html=True)
                            except Exception as format_err:
                                print(f"Error al formatear las citas: {str(format_err)}")
                                st.markdown(response)  # Mostrar sin formato en caso de error
                        else:
                            st.markdown(response)
                        
                        # Mostrar las citas si existen en los expanders
                        if citations:
                            with st.expander("Ver referencias"):
                                for i, citation in enumerate(citations):
                                    # Eliminar las extensiones del título del documento
                                    document_title = citation['document_title']
                                    document_title = document_title.replace('.pdf', '').replace('.html', '')
                                    # Mostrar el documento con su índice de origen
                                    index_name = ""
                                    if "source_index" in citation:
                                        index_name = f" [{citation['source_index']}]"
                                    st.markdown(f"**[{i+1}]** `{document_title}{index_name}`")
                                    st.markdown(f"*\"{citation['cited_text']}\"*")
                        
                        # Mostrar las fuentes utilizadas
                        with st.expander("Ver fuentes utilizadas"):
                            for i, doc in enumerate(documents):
                                source = doc.metadata.get('source', f'Documento {i+1}')
                                # Eliminar las extensiones del nombre de la fuente
                                source = source.replace('.pdf', '').replace('.html', '')
                                # Limpiar prefijos comunes de la fuente
                                prefixes_to_remove = [
                                    "pinecone_docs/", "Pinecone: ",
                                    "pinecone_timbre/data/timbre/", "pinecone_renta/data/renta/",
                                    "pinecone_iva/data/iva/", "pinecone_retencion/data/retencion/",
                                    "pinecone_ipoconsumo/data/ipoconsumo/", "pinecone_aduanas/data/aduanas/",
                                    "pinecone_cambiario/data/cambiario/", "pinecone_ica/data/ica/",
                                    "data/timbre/", "data/renta/", "data/iva/", "data/ica/",
                                    "data/retencion/", "data/ipoconsumo/", "data/aduanas/", "data/cambiario/"
                                ]
                                for prefix in prefixes_to_remove:
                                    if prefix in source:
                                        source = source.replace(prefix, "")
                                # Aplicar expresión regular general para cualquier otro prefijo de tipo data/XXX/
                                source = re.sub(r'(?:^|/)data/\w+/', '', source)
                                # Mostrar el índice de origen si está disponible
                                index_name = doc.metadata.get('source_index', '')
                                index_info = f" [{index_name}]" if index_name else ""
                                page = doc.metadata.get('page', None)
                                page_info = f" (Pág. {page})" if page and page != 0 else ""
                                st.markdown(f"**Fuente {i+1}:** `{source}{index_info}{page_info}`")
                                st.markdown(f"```\n{doc.page_content}\n```")
                        
                        # Mostrar los índices utilizados
                        if indices_used:
                            with st.expander("Índices consultados"):
                                st.markdown("##### Índices de donde proviene la información:")
                                for index in indices_used:
                                    st.markdown(f"- {index}")
                        
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
                    indices_used = []
            
            # Agregar la respuesta del asistente a los mensajes
            st.session_state.general_messages.append({
                "role": "assistant", 
                "content": response,
                "documents": documents if 'documents' in locals() else [],
                "flow": final_flow if 'final_flow' in locals() else '',
                "citations": citations if 'citations' in locals() else [],
                "indices_used": indices_used if 'indices_used' in locals() else []
            })

except Exception as e:
    st.error(f"Error al conectar con Pinecone: {str(e)}") 