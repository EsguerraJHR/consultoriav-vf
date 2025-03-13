# Asistente Jurídico Tributario

Aplicación de asistencia jurídica tributaria que utiliza técnicas avanzadas de Retrieval Augmented Generation (RAG) para proporcionar respuestas precisas a consultas jurídicas en el área de derecho tributario colombiano.

## Características

- **Interfaz de usuario intuitiva**: Aplicación web desarrollada con Streamlit
- **Respuestas fundamentadas**: Basadas en documentos oficiales de la DIAN
- **Biblioteca de documentos**: 
  - Renta: Documentos sobre el Impuesto de Renta
  - Timbre: Documentos sobre el Impuesto de Timbre
  - Retencion: Documentos sobre Retención en la Fuente
- **Verificación de fuentes**:
  - Acceso directo a los documentos citados en las respuestas
  - Organización por categorías tributarias
  - Trazabilidad de la información jurídica
- **Buzón de Observaciones**: Sistema para recibir comentarios y sugerencias de los usuarios

## Estructura del Proyecto

- `Inicio.py`: Página principal con descripción general de la aplicación
- `pages/`: Directorio con páginas adicionales de la aplicación
  - `2_Renta.py`: Página para consultas sobre Impuesto de Renta
  - `3_Timbre.py`: Página para consultas sobre Impuesto de Timbre
  - `4_Retencion.py`: Página para consultas sobre Retención en la Fuente
  - `5_Biblioteca.py`: Página para acceder a los documentos jurídicos
  - `6_Buzón_de_Observaciones.py`: Página para enviar comentarios y sugerencias
- `pages_hidden/`: Directorio con páginas ocultas (no visibles en la interfaz)
  - `1_Dian_varios.py`: Página para consultas sobre conceptos de la Dian (oculta)
- `graph/`: Directorio con definiciones de grafos LangGraph
- `legal_docs/`: Documentos legales utilizados para entrenamiento
- `.chroma/`: Base de datos vectorial local (Chroma)
- `data/`: Datos adicionales para la aplicación

## Requisitos

- Python 3.10 o superior
- Poetry (gestor de dependencias)
- Claves API para:
  - OpenAI
  - Anthropic (opcional)
  - Pinecone
  - Tavily (opcional)
  - LangChain (opcional para trazabilidad)
- Cuenta de correo electrónico (para el buzón de observaciones)

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/asistente-juridico-tributario.git
   cd asistente-juridico-tributario
   ```

2. Instala las dependencias con Poetry:
   ```
   poetry install
   ```

3. Crea un archivo `.env` con tus claves API (usa `.env.example` como referencia)

## Ejecución

1. Activa el entorno virtual:
   ```
   poetry shell
   ```

2. Inicia la aplicación Streamlit:
   ```
   streamlit run Inicio.py
   ```

3. Abre tu navegador en `http://localhost:8501`

## Próximas Funcionalidades

- **Búsqueda avanzada**: Filtros adicionales y búsqueda por contenido del documento
- **Exportación masiva**: Posibilidad de descargar múltiples documentos a la vez
- **Anotaciones**: Herramientas para que los abogados puedan agregar notas a los documentos
- **Integración con respuestas**: Acceso directo a los documentos citados en cada respuesta

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Ver el archivo `LICENSE` para más detalles.