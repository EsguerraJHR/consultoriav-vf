import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Asistente Jurídico Tributario",
    page_icon="📚",
    layout="wide"
)

# Crear una fila para el logo y el título
col1, col2 = st.columns([1, 4])

# Cargar y mostrar la imagen local en la columna izquierda
with col1:
    image = Image.open("EJHR.AI.png")
    st.image(image, width=100)

# Título principal en la columna derecha
with col2:
    st.markdown("<h1 style='text-align: left;'>Asistente Jurídico Tributario</h1>", unsafe_allow_html=True)

# Descripción concisa de la aplicación
st.markdown("""
## Asistente de Derecho Tributario

Esta aplicación utiliza tecnología avanzada de Inteligencia Artificial para proporcionar 
respuestas precisas a consultas jurídicas en el área de derecho tributario colombiano.

### Características principales:

- **Respuestas fundamentadas**: Todas las respuestas están basadas en documentos oficiales de la DIAN
- **Referencias precisas**: Cada respuesta incluye citas a las fuentes utilizadas
- **Verificación de información**: Acceso a los documentos originales para validar las respuestas

Utilice la barra lateral para navegar entre las diferentes secciones de la aplicación.
""")

# Sección de cómo funciona
with st.expander("¿Cómo funciona?"):
    st.markdown("""
    1. **Consulta**: El usuario realiza una pregunta sobre derecho tributario colombiano
    2. **Procesamiento**: El sistema busca documentos relevantes en nuestra base de datos
    3. **Generación**: Se crea una respuesta fundamentada en los documentos encontrados
    4. **Verificación**: El usuario puede acceder a los documentos citados para validar la información
    
    Nuestra tecnología RAG (Retrieval Augmented Generation) combina la potencia de los modelos de lenguaje
    con una base de conocimiento especializada en derecho tributario colombiano.
    """)

# Sección de áreas cubiertas
with st.expander("Áreas cubiertas"):
    st.markdown("""
    - **Impuesto de Renta**: Conceptos, normativa y jurisprudencia desde 2017 hasta 2024
    - **Impuesto de Timbre**: Documentación oficial y conceptos desde 2017 hasta 2024
    - **Retención en la Fuente**: Normativa y conceptos desde 2017 hasta 2024
    """)

# Agregar un footer
st.markdown("""
---
<div style="text-align: center; color: gray; font-size: 0.8em;">
© 2025 Asistente Jurídico Tributario | Desarrollado con tecnología RAG
</div>
""", unsafe_allow_html=True)