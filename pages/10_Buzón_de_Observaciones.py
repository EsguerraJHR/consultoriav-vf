import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import datetime
import csv
import io
import requests
import base64
import json

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Buzón de Observaciones",
    page_icon="📬",
    layout="wide"
)

# Título de la página
st.title("📬 Buzón de Observaciones")

# Descripción de la página
st.markdown("""
Agradecemos sus comentarios para mejorar nuestro Asistente Jurídico Tributario.
Por favor, comparta sus observaciones, sugerencias o reporte cualquier problema que haya encontrado.

Todas las observaciones son confidenciales y solo serán revisadas por el administrador del sistema.
""")

# Función para guardar observaciones en GitHub
def guardar_observaciones_en_github(observaciones):
    try:
        # Configuración de GitHub desde variables de entorno
        github_token = os.environ.get("GITHUB_TOKEN", "")
        repo_owner = os.environ.get("GITHUB_REPO_OWNER", "EsguerraJHR")
        repo_name = os.environ.get("GITHUB_REPO_NAME", "consultoriav-vf")
        file_path = os.environ.get("GITHUB_FILE_PATH", "data/observaciones.csv")
        
        # Verificar si tenemos un token
        if not github_token:
            st.warning("No se ha configurado el token de GitHub. Las observaciones se guardarán solo en la sesión actual.")
            return False
        
        # Convertir la lista de observaciones a DataFrame y luego a CSV
        df = pd.DataFrame(observaciones)
        
        # Si no hay observaciones, crear un DataFrame vacío con las columnas correctas
        if df.empty:
            df = pd.DataFrame(columns=['Fecha', 'Nombre', 'Correo', 'Tipo', 'Asunto', 'Mensaje'])
        
        csv_content = df.to_csv(index=False)
        
        # URL de la API de GitHub para obtener el contenido actual del archivo
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        
        # Configurar headers con el token de autenticación
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Verificar si el archivo ya existe
        response = requests.get(url, headers=headers)
        
        # Preparar el contenido codificado en base64
        encoded_content = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
        
        # Datos para la solicitud
        data = {
            "message": "Actualizar observaciones",
            "content": encoded_content,
        }
        
        # Si el archivo existe, necesitamos su SHA para actualizarlo
        if response.status_code == 200:
            data["sha"] = response.json()["sha"]
            
            # Realizar la solicitud para actualizar el archivo
            response = requests.put(url, headers=headers, data=json.dumps(data))
            
            if response.status_code in [200, 201]:
                return True
            else:
                st.error(f"Error al actualizar el archivo: {response.status_code} - {response.text}")
                return False
        elif response.status_code == 404:
            # Si el archivo no existe, primero verificar si la carpeta data existe
            folder_parts = file_path.split('/')
            if len(folder_parts) > 1:
                folder_path = '/'.join(folder_parts[:-1])
                
                # Verificar si la carpeta existe
                folder_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
                folder_response = requests.get(folder_url, headers=headers)
                
                # Si la carpeta no existe, intentar crearla
                if folder_response.status_code == 404:
                    st.info(f"La carpeta {folder_path} no existe. Creando archivo directamente...")
            
            # Crear el archivo
            response = requests.put(url, headers=headers, data=json.dumps(data))
            
            if response.status_code in [200, 201]:
                return True
            else:
                st.error(f"Error al crear el archivo: {response.status_code} - {response.text}")
                return False
        else:
            st.error(f"Error al verificar el archivo: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Error al guardar observaciones: {str(e)}")
        return False

# Función para guardar observaciones (con respaldo en sesión)
def guardar_observacion(nueva_observacion):
    # Agregar la observación a la lista en el estado de la sesión
    st.session_state.observaciones.append(nueva_observacion)
    
    # Intentar guardar en GitHub
    exito = guardar_observaciones_en_github(st.session_state.observaciones)
    
    # Incluso si falla GitHub, la observación se guarda en la sesión
    if not exito:
        st.warning("La observación se ha guardado en la sesión actual, pero no se pudo guardar en GitHub. Las observaciones se perderán al reiniciar la aplicación.")
    
    return True

# Función para cargar observaciones desde GitHub
def cargar_observaciones_desde_github():
    try:
        # Configuración de GitHub desde variables de entorno
        github_token = os.environ.get("GITHUB_TOKEN", "")
        repo_owner = os.environ.get("GITHUB_REPO_OWNER", "EsguerraJHR")
        repo_name = os.environ.get("GITHUB_REPO_NAME", "consultoriav-vf")
        file_path = os.environ.get("GITHUB_FILE_PATH", "data/observaciones.csv")
        
        # Verificar si tenemos un token
        if not github_token:
            st.warning("No se ha configurado el token de GitHub. Las observaciones se guardarán solo en la sesión actual.")
            return []
        
        # URL de la API de GitHub para obtener el contenido del archivo
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        
        # Configurar headers con el token de autenticación
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Realizar la solicitud a la API de GitHub
        response = requests.get(url, headers=headers)
        
        # Si el archivo existe, decodificar su contenido
        if response.status_code == 200:
            content = response.json()
            file_content = base64.b64decode(content["content"]).decode("utf-8")
            
            # Convertir el contenido CSV a DataFrame
            df = pd.read_csv(io.StringIO(file_content))
            return df.to_dict('records')  # Convertir DataFrame a lista de diccionarios
        elif response.status_code == 404:
            # Si el archivo no existe, intentar crear la carpeta data y un archivo vacío
            st.info("No se encontró el archivo de observaciones. Se creará uno nuevo.")
            return []
        else:
            st.warning(f"Error al acceder a GitHub: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.warning(f"Error al cargar observaciones: {str(e)}")
        return []

# Inicializar la lista de observaciones
if 'observaciones' not in st.session_state:
    # Intentar cargar observaciones desde GitHub
    github_observaciones = cargar_observaciones_desde_github()
    
    # Si hay observaciones en GitHub, usarlas; de lo contrario, inicializar una lista vacía
    if github_observaciones:
        st.session_state.observaciones = github_observaciones
        st.success("Observaciones cargadas correctamente desde GitHub.")
    else:
        st.session_state.observaciones = []
        st.info("No se pudieron cargar observaciones desde GitHub. Se usará almacenamiento en sesión.")

# Inicializar el estado de envío
if 'observacion_enviada' not in st.session_state:
    st.session_state.observacion_enviada = False

# Mostrar mensaje de éxito si se ha enviado una observación
if st.session_state.observacion_enviada:
    st.success("¡Gracias por sus observaciones! Su mensaje ha sido registrado correctamente.")
    
    # Botón para enviar otra observación
    if st.button("Enviar otra observación"):
        st.session_state.observacion_enviada = False
        st.rerun()
else:
    # Formulario para enviar observaciones
    with st.form("observaciones_form"):
        st.subheader("Formulario de Observaciones")
        
        # Campos del formulario con descripciones
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo", 
                                help="Ingrese su nombre completo para que podamos dirigirnos a usted correctamente")
        
        with col2:
            correo = st.text_input("Correo electrónico", 
                                help="Su correo electrónico nos permitirá contactarlo si necesitamos más información")
        
        tipo_observacion = st.selectbox(
            "Tipo de observación",
            ["Sugerencia", "Reporte de error", "Pregunta", "Comentario general"],
            help="Seleccione el tipo de observación que mejor describe su mensaje"
        )
        
        asunto = st.text_input("Asunto", 
                            help="Un breve título que resuma su observación")
        
        mensaje = st.text_area("Mensaje", height=200, 
                            help="Describa su observación, sugerencia o problema con el mayor detalle posible")
        
        # Botón de envío
        submitted = st.form_submit_button("Enviar observación", use_container_width=True)
        
        if submitted:
            # Validar campos
            if not nombre or not correo or not asunto or not mensaje:
                st.error("Por favor, complete todos los campos.")
            elif "@" not in correo:
                st.error("Por favor, ingrese un correo electrónico válido.")
            else:
                try:
                    # Obtener la fecha y hora actual
                    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Crear un diccionario con la observación
                    nueva_observacion = {
                        'Fecha': fecha_actual,
                        'Nombre': nombre,
                        'Correo': correo,
                        'Tipo': tipo_observacion,
                        'Asunto': asunto,
                        'Mensaje': mensaje
                    }
                    
                    # Guardar la observación (con respaldo en sesión)
                    guardar_observacion(nueva_observacion)
                    
                    # Marcar como enviada
                    st.session_state.observacion_enviada = True
                    
                    # Recargar la página
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error al guardar la observación: {str(e)}")
                    st.info("La observación no se ha podido guardar. Por favor, inténtelo de nuevo más tarde.")

# Información adicional
st.markdown("""
---
## Información de contacto

Si prefiere contactarnos directamente, puede hacerlo a través de:

- **Correo electrónico**: hcastro@esguerrajhr.com
- **Teléfono**: +57 (601) 744-7700

Valoramos sus comentarios y trabajamos constantemente para mejorar nuestro servicio.
""")

# Sección para administradores (oculta por defecto)
with st.expander("Acceso Administrativo (Solo para Hernando Castro)", expanded=False):
    st.write("Esta sección es exclusiva para el administrador del sistema.")
    
    # Nota sobre el almacenamiento persistente
    st.info("""
    Las observaciones se almacenan de forma persistente en un archivo CSV en el repositorio de GitHub.
    Puedes acceder a ellas en cualquier momento, incluso después de reiniciar la aplicación.
    """)
    
    # Contraseña para acceder a las observaciones (más segura)
    admin_password = st.text_input("Contraseña de administrador", type="password")
    
    # Usar una contraseña más segura
    if admin_password == "EJHRtributario2025":  # Reemplaza esto con tu contraseña real
        st.success("Acceso concedido. Bienvenido, Hernando.")
        
        # Botón para recargar observaciones desde GitHub
        if st.button("Recargar observaciones desde GitHub"):
            st.session_state.observaciones = cargar_observaciones_desde_github()
            st.success(f"Se han cargado {len(st.session_state.observaciones)} observaciones desde GitHub.")
            st.rerun()
        
        # Mostrar las observaciones
        if st.session_state.observaciones:
            # Convertir la lista de observaciones a un DataFrame
            observaciones_df = pd.DataFrame(st.session_state.observaciones)
            
            st.write(f"Total de observaciones: {len(observaciones_df)}")
            
            # Agregar filtros para las observaciones
            st.subheader("Filtros")
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Tipo' in observaciones_df.columns:
                    tipos_unicos = ["Todos"] + list(observaciones_df['Tipo'].unique())
                    tipo_filtro = st.selectbox("Filtrar por tipo", tipos_unicos)
            
            with col2:
                if 'Fecha' in observaciones_df.columns:
                    fechas_unicas = ["Todas"] + list(observaciones_df['Fecha'].str.split(' ').str[0].unique())
                    fecha_filtro = st.selectbox("Filtrar por fecha", fechas_unicas)
            
            # Aplicar filtros
            df_filtrado = observaciones_df.copy()
            if tipo_filtro != "Todos" and 'Tipo' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_filtro]
            
            if fecha_filtro != "Todas" and 'Fecha' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Fecha'].str.contains(fecha_filtro)]
            
            # Mostrar DataFrame filtrado
            st.dataframe(df_filtrado)
            
            # Opción para descargar las observaciones como CSV
            csv_buffer = io.StringIO()
            observaciones_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue().encode('utf-8')
            
            st.download_button(
                label="Descargar todas las observaciones como CSV",
                data=csv_data,
                file_name=f"observaciones_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # También permitir descargar solo las observaciones filtradas
            if tipo_filtro != "Todos" or fecha_filtro != "Todas":
                csv_buffer_filtrado = io.StringIO()
                df_filtrado.to_csv(csv_buffer_filtrado, index=False)
                csv_data_filtrado = csv_buffer_filtrado.getvalue().encode('utf-8')
                
                st.download_button(
                    label="Descargar observaciones filtradas como CSV",
                    data=csv_data_filtrado,
                    file_name=f"observaciones_filtradas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_filtered"
                )
            
            # Mostrar observaciones en formato de texto para copiar manualmente
            with st.expander("Ver observaciones en formato de texto (para copiar)"):
                # Crear un formato de texto más legible
                texto_observaciones = ""
                for _, obs in df_filtrado.iterrows():
                    texto_observaciones += f"Fecha: {obs['Fecha']}\n"
                    texto_observaciones += f"Nombre: {obs['Nombre']}\n"
                    texto_observaciones += f"Correo: {obs['Correo']}\n"
                    texto_observaciones += f"Tipo: {obs['Tipo']}\n"
                    texto_observaciones += f"Asunto: {obs['Asunto']}\n"
                    texto_observaciones += f"Mensaje: {obs['Mensaje']}\n"
                    texto_observaciones += "-" * 50 + "\n"
                
                st.text_area("Selecciona todo este texto y cópialo (Ctrl+C o Cmd+C)", 
                             texto_observaciones, 
                             height=300)
                st.info("Puedes seleccionar todo el texto de arriba, copiarlo y pegarlo en un correo electrónico o documento.")
            
            # Opción para eliminar todas las observaciones
            st.subheader("Administración de observaciones")
            if st.button("Eliminar todas las observaciones", type="primary", use_container_width=True):
                confirmacion = st.text_input("Para confirmar, escribe 'ELIMINAR'")
                if confirmacion == "ELIMINAR":
                    # Vaciar la lista de observaciones
                    st.session_state.observaciones = []
                    
                    # Guardar la lista vacía en GitHub
                    exito = guardar_observaciones_en_github(st.session_state.observaciones)
                    
                    if exito:
                        st.success("Todas las observaciones han sido eliminadas permanentemente.")
                        st.rerun()
                    else:
                        st.error("No se pudieron eliminar las observaciones de forma permanente. Por favor, inténtelo de nuevo más tarde.")
                elif confirmacion:
                    st.error("Texto de confirmación incorrecto. Las observaciones no han sido eliminadas.")
        else:
            st.info("No hay observaciones registradas.")
    elif admin_password and admin_password != "EJHRtributario2025":
        st.error("Contraseña incorrecta. Acceso denegado.")

# Agregar un footer
st.markdown("""
---
<div style="text-align: center; color: gray; font-size: 0.8em;">
© 2025 Asistente Jurídico Tributario | Desarrollado con tecnología RAG
</div>
""", unsafe_allow_html=True) 