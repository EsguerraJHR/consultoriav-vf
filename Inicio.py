import streamlit as st
from dotenv import load_dotenv
import os
from graph.graph import app, set_debug
import time
import re

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Asistente Jurídico Tributario",
    page_icon="⚖️",
    layout="wide"
)

# Título de la página en la barra lateral (esto cambiará el nombre de la pestaña)
st.sidebar.title("")

# Desactivar la depuración en consola
set_debug(True)

# Función para obtener la colección adecuada según la subárea
def obtener_coleccion(subarea=None):
    # Para mantener compatibilidad con la estructura actual
    if subarea == "Dian varios":
        return "legal-docs-chroma"  # Usa la colección existente
    
    # Para nuevas subáreas (futuras implementaciones)
    if subarea:
        return f"derecho_tributario-{subarea.lower().replace(' ', '_')}-chroma"
    else:
        return "derecho_tributario-chroma"

# Verificar si una colección existe
def verificar_coleccion(subarea=None):
    collection_name = obtener_coleccion(subarea)
    chroma_dir = "./.chroma"
    
    # Verificar si la carpeta .chroma existe
    if not os.path.exists(chroma_dir):
        return False
    
    # Caso especial para Renta (usa Pinecone)
    if subarea == "Renta":
        print("verificar_coleccion: Verificando Pinecone para Renta")
        # Siempre devolver True para Renta, ya que forzaremos el uso de Pinecone
        return True
    
    # Caso especial para Timbre (usa Pinecone)
    if subarea == "Timbre":
        print("verificar_coleccion: Verificando Pinecone para Timbre")
        # Siempre devolver True para Timbre, ya que forzaremos el uso de Pinecone
        return True
    
    # Caso especial para Retencion (usa Pinecone)
    if subarea == "Retencion":
        print("verificar_coleccion: Verificando Pinecone para Retencion")
        # Siempre devolver True para Retencion, ya que forzaremos el uso de Pinecone
        return True
    
    # Intentar acceder a la colección (implementación básica)
    # En una implementación completa, verificaríamos si la colección existe en Chroma
    if collection_name == "legal-docs-chroma":
        return True  # Asumimos que la colección principal existe
    
    # Para otras colecciones, verificar si ya se han creado (futuras implementaciones)
    return False

# Función para formatear el texto con citas numeradas
def formatear_texto_con_citas(texto, citas):
    """
    Ya no necesitamos formatear el texto con citas, ya que Claude las incluye directamente.
    Esta función ahora solo se asegura de que las citas se muestren correctamente en HTML.
    """
    if not citas:
        return texto
    
    # Reemplazar los corchetes de cita por etiquetas HTML para mejorar la visualización
    texto_formateado = re.sub(r'\[(\d+)\]', r'<sup>[\1]</sup>', texto)
    
    return texto_formateado

# Inicializar estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Obtener parámetros de URL para mantener el estado entre recargas
query_params = st.query_params
default_subarea = query_params.get("subarea", ["IVA"])[0] if "subarea" in query_params else "IVA"

# Verificar que la subárea exista en nuestras opciones
if default_subarea not in ["Renta", "Timbre", "Retencion"]:
    default_subarea = "Renta"

# Inicializar o actualizar el estado con los valores de URL
if "subarea_seleccionada" not in st.session_state:
    st.session_state.subarea_seleccionada = default_subarea

# Título principal
st.title("⚖️ Asistente Jurídico Tributario")

# Tabs para las subáreas
tab1, tab2, tab3 = st.tabs(["Renta", "Timbre", "Retencion"])

with tab1:
    st.markdown("""
    ### Documentos de Renta
    
    En esta sección encontrará los documentos citados en las respuestas relacionadas con el Impuesto de Renta.
    
    *Próximamente: Acceso directo a los documentos citados para verificación de la información.*
    """)

with tab2:
    st.markdown("""
    ### Documentos de Timbre
    
    En esta sección encontrará los documentos citados en las respuestas relacionadas con el Impuesto de Timbre.
    
    *Próximamente: Acceso directo a los documentos citados para verificación de la información.*
    """)

with tab3:
    st.markdown("""
    ### Documentos de Retención en la Fuente
    
    En esta sección encontrará los documentos citados en las respuestas relacionadas con Retención en la Fuente.
    
    *Próximamente: Acceso directo a los documentos citados para verificación de la información.*
    """)

# Descripción de la aplicación
st.markdown(f"""
## Asistente de Derecho Tributario

Esta aplicación utiliza técnicas avanzadas de Retrieval Augmented Generation (RAG) para proporcionar 
respuestas precisas a consultas jurídicas en el área de derecho tributario colombiano.

### Verificación de Fuentes

Nuestro sistema genera respuestas basadas en documentos oficiales y proporciona referencias precisas a las fuentes utilizadas.
Los abogados podrán verificar la información directamente accediendo a los documentos citados en cada respuesta.

En las pestañas superiores, próximamente encontrará acceso a los documentos organizados por categoría:

- **Renta**: Documentos sobre el Impuesto de Renta desde enero de 2017 hasta diciembre de 2024 (Pinecone)
- **Timbre**: Documentos sobre el Impuesto de Timbre desde enero de 2017 hasta diciembre de 2024 (Pinecone)
- **Retencion**: Documentos sobre Retención en la Fuente desde enero de 2017 hasta diciembre de 2024 (Pinecone)

Esta funcionalidad permitirá a los profesionales del derecho verificar la precisión de las respuestas generadas
y profundizar en el análisis de las fuentes jurídicas relevantes.
""")

# Agregar una sección de próximos pasos
st.markdown("""
---
## Próximos Pasos

En futuras actualizaciones, implementaremos:

1. **Acceso directo a documentos**: Navegación y búsqueda en la base documental.
2. **Verificación de citas**: Sistema para validar las referencias utilizadas en las respuestas.
3. **Exportación de documentos**: Posibilidad de descargar los documentos citados.
4. **Anotaciones**: Herramientas para que los abogados puedan agregar notas a los documentos.

Estamos trabajando para proporcionar una herramienta completa que facilite la investigación jurídica tributaria.
""")

# Agregar un footer
st.markdown("""
---
<div style="text-align: center; color: gray; font-size: 0.8em;">
© 2024 Asistente Jurídico Tributario | Desarrollado con tecnología RAG
</div>
""", unsafe_allow_html=True)