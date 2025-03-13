import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import re

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Biblioteca Jurídica",
    page_icon="📚",
    layout="wide"
)

# Título principal
st.title("📚 Biblioteca Jurídica Tributaria")

# Descripción de la página
st.markdown("""
Esta sección le permite acceder a los documentos oficiales utilizados como fuentes en las respuestas generadas.
Puede explorar los documentos por categoría, realizar búsquedas y verificar la información citada. Esta función será funcional en la versión final. Por ahora podrán acceder a los documentos aquí [Biblioteca](https://eba-my.sharepoint.com/:f:/g/personal/hcastro_esguerrajhr_com/EgWozji9P89Gi02QG_0ybskBFzI39tnYkn78gfP3PiGWPw?e=JCZUDU).
""")

# Crear pestañas para las diferentes categorías
tab1, tab2, tab3, tab4 = st.tabs(["Renta", "Timbre", "Retención", "IVA"])

# Función para mostrar documentos de ejemplo
def mostrar_documentos_ejemplo(categoria, num_docs=10):
    # En una implementación real, estos datos vendrían de una base de datos
    años = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]
    tipos = ["Concepto", "Oficio", "Resolución", "Circular"]
    
    # Crear datos de ejemplo
    data = []
    for i in range(num_docs):
        año = años[i % len(años)]
        tipo = tipos[i % len(tipos)]
        numero = f"{10000 + i*1111}"
        titulo = f"{tipo} {numero} de {año} - {categoria}"
        data.append({
            "Año": año,
            "Tipo": tipo,
            "Número": numero,
            "Título": titulo,
            "Categoría": categoria
        })
    
    return pd.DataFrame(data)

# Contenido para la pestaña de Renta
with tab1:
    st.header("Documentos sobre Impuesto de Renta")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        año_renta = st.selectbox("Año", ["Todos", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017"], key="año_renta")
    with col2:
        tipo_renta = st.selectbox("Tipo de documento", ["Todos", "Concepto", "Oficio", "Resolución", "Circular"], key="tipo_renta")
    with col3:
        busqueda_renta = st.text_input("Buscar por palabra clave", key="busqueda_renta")
    
    # Mostrar documentos de ejemplo
    df_renta = mostrar_documentos_ejemplo("Renta")
    
    # Aplicar filtros (simulado)
    if año_renta != "Todos":
        df_renta = df_renta[df_renta["Año"] == año_renta]
    if tipo_renta != "Todos":
        df_renta = df_renta[df_renta["Tipo"] == tipo_renta]
    if busqueda_renta:
        df_renta = df_renta[df_renta["Título"].str.contains(busqueda_renta, case=False)]
    
    # Mostrar tabla de documentos
    st.dataframe(df_renta, use_container_width=True)
    
    # Previsualización de documento
    st.subheader("Previsualización del documento")
    documento_seleccionado = st.selectbox("Seleccione un documento para previsualizar", df_renta["Título"].tolist(), key="doc_renta")
    
    if documento_seleccionado:
        with st.expander("Ver contenido del documento", expanded=True):
            st.markdown(f"### {documento_seleccionado}")
            st.markdown("""
            **Extracto del documento:**
            
            Considerando que el artículo 240 del Estatuto Tributario, modificado por el artículo 7 de la Ley 2277 de 2022, 
            establece la tarifa general del impuesto sobre la renta aplicable a las personas jurídicas, la cual será del 
            35% para el año gravable 2023 y siguientes.
            
            Que, adicionalmente, el parágrafo 1 del mismo artículo señala que las instituciones financieras deberán 
            liquidar unos puntos adicionales al impuesto sobre la renta y complementarios cuando la renta gravable sea 
            igual o superior a 120.000 UVT.
            
            Por lo tanto, se concluye que...
            """)
            
            st.download_button(
                label="Descargar documento completo",
                data="Contenido completo del documento en formato PDF",
                file_name=f"{documento_seleccionado}.pdf",
                mime="application/pdf",
                disabled=True  # Deshabilitado en este MVP
            )

# Contenido para la pestaña de Timbre
with tab2:
    st.header("Documentos sobre Impuesto de Timbre")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        año_timbre = st.selectbox("Año", ["Todos", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017"], key="año_timbre")
    with col2:
        tipo_timbre = st.selectbox("Tipo de documento", ["Todos", "Concepto", "Oficio", "Resolución", "Circular"], key="tipo_timbre")
    with col3:
        busqueda_timbre = st.text_input("Buscar por palabra clave", key="busqueda_timbre")
    
    # Mostrar documentos de ejemplo
    df_timbre = mostrar_documentos_ejemplo("Timbre")
    
    # Aplicar filtros (simulado)
    if año_timbre != "Todos":
        df_timbre = df_timbre[df_timbre["Año"] == año_timbre]
    if tipo_timbre != "Todos":
        df_timbre = df_timbre[df_timbre["Tipo"] == tipo_timbre]
    if busqueda_timbre:
        df_timbre = df_timbre[df_timbre["Título"].str.contains(busqueda_timbre, case=False)]
    
    # Mostrar tabla de documentos
    st.dataframe(df_timbre, use_container_width=True)
    
    # Mensaje de funcionalidad en desarrollo
    st.info("La previsualización de documentos de Timbre estará disponible próximamente.")

# Contenido para la pestaña de Retención
with tab3:
    st.header("Documentos sobre Retención en la Fuente")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        año_retencion = st.selectbox("Año", ["Todos", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017"], key="año_retencion")
    with col2:
        tipo_retencion = st.selectbox("Tipo de documento", ["Todos", "Concepto", "Oficio", "Resolución", "Circular"], key="tipo_retencion")
    with col3:
        busqueda_retencion = st.text_input("Buscar por palabra clave", key="busqueda_retencion")
    
    # Mostrar documentos de ejemplo
    df_retencion = mostrar_documentos_ejemplo("Retención")
    
    # Aplicar filtros (simulado)
    if año_retencion != "Todos":
        df_retencion = df_retencion[df_retencion["Año"] == año_retencion]
    if tipo_retencion != "Todos":
        df_retencion = df_retencion[df_retencion["Tipo"] == tipo_retencion]
    if busqueda_retencion:
        df_retencion = df_retencion[df_retencion["Título"].str.contains(busqueda_retencion, case=False)]
    
    # Mostrar tabla de documentos
    st.dataframe(df_retencion, use_container_width=True)
    
    # Mensaje de funcionalidad en desarrollo
    st.info("La previsualización de documentos de Retención estará disponible próximamente.")

# Contenido para la pestaña de IVA
with tab4:
    st.header("Documentos sobre Impuesto al Valor Agregado (IVA)")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        año_iva = st.selectbox("Año", ["Todos", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017"], key="año_iva")
    with col2:
        tipo_iva = st.selectbox("Tipo de documento", ["Todos", "Concepto", "Oficio", "Resolución", "Circular"], key="tipo_iva")
    with col3:
        busqueda_iva = st.text_input("Buscar por palabra clave", key="busqueda_iva")
    
    # Mostrar documentos de ejemplo
    df_iva = mostrar_documentos_ejemplo("IVA")
    
    # Aplicar filtros (simulado)
    if año_iva != "Todos":
        df_iva = df_iva[df_iva["Año"] == año_iva]
    if tipo_iva != "Todos":
        df_iva = df_iva[df_iva["Tipo"] == tipo_iva]
    if busqueda_iva:
        df_iva = df_iva[df_iva["Título"].str.contains(busqueda_iva, case=False)]
    
    # Mostrar tabla de documentos
    st.dataframe(df_iva, use_container_width=True)
    
    # Mensaje de funcionalidad en desarrollo
    st.info("La previsualización de documentos de IVA estará disponible próximamente.")

# Sección de próximas funcionalidades
st.markdown("""
---
## Próximas funcionalidades

En futuras actualizaciones, implementaremos:

1. **Búsqueda avanzada**: Filtros adicionales y búsqueda por contenido del documento
2. **Exportación masiva**: Posibilidad de descargar múltiples documentos a la vez
3. **Anotaciones**: Herramientas para que los abogados puedan agregar notas a los documentos
4. **Integración con respuestas**: Acceso directo a los documentos citados en cada respuesta

Estamos trabajando para proporcionar una herramienta completa que facilite la investigación jurídica tributaria.
""")

# Agregar un footer
st.markdown("""
---
<div style="text-align: center; color: gray; font-size: 0.8em;">
© 2025 Asistente Jurídico Tributario | Biblioteca Jurídica Tributaria
</div>
""", unsafe_allow_html=True) 