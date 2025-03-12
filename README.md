# Asistente Jurídico Tributario

Aplicación de asistencia jurídica tributaria que utiliza técnicas avanzadas de Retrieval Augmented Generation (RAG) para proporcionar respuestas precisas a consultas jurídicas en el área de derecho tributario colombiano.

## Características

- **Interfaz de usuario intuitiva**: Aplicación web desarrollada con Streamlit
- **Acceso a documentos oficiales**: 
  - Renta: Documentos sobre el Impuesto de Renta
  - Timbre: Documentos sobre el Impuesto de Timbre
  - Retencion: Documentos sobre Retención en la Fuente
- **Verificación de fuentes**:
  - Acceso directo a los documentos citados en las respuestas
  - Organización por categorías tributarias
  - Trazabilidad de la información jurídica

## Estructura del Proyecto

- `Inicio.py`: Página principal de la aplicación Streamlit
- `pages/`: Directorio con páginas adicionales de la aplicación
  - `2_Renta.py`: Página para acceder a documentos sobre Impuesto de Renta
  - `3_Timbre.py`: Página para acceder a documentos sobre Impuesto de Timbre
  - `4_Retencion.py`: Página para acceder a documentos sobre Retención en la Fuente
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

- **Acceso directo a documentos**: Navegación y búsqueda en la base documental
- **Verificación de citas**: Sistema para validar las referencias utilizadas en las respuestas
- **Exportación de documentos**: Posibilidad de descargar los documentos citados
- **Anotaciones**: Herramientas para que los abogados puedan agregar notas a los documentos

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Ver el archivo `LICENSE` para más detalles.