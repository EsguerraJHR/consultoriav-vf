# Implementación de Pinecone con text-embedding-3-large

Este proyecto implementa un sistema de búsqueda semántica para documentos de renta utilizando Pinecone como base de datos vectorial y el modelo text-embedding-3-large de OpenAI para generar embeddings.

## Requisitos previos

1. Cuenta en [Pinecone](https://www.pinecone.io/)
2. Cuenta en [OpenAI](https://openai.com/)
3. Python 3.8 o superior
4. Poetry (gestor de dependencias)

## Configuración

### 1. Crear una cuenta en Pinecone

Si aún no tienes una cuenta en Pinecone, regístrate en [https://www.pinecone.io/](https://www.pinecone.io/).

### 2. Crear un índice en Pinecone

1. Inicia sesión en la consola de Pinecone
2. Crea un nuevo índice con las siguientes especificaciones:
   - Nombre: `renta-docs` (o el nombre que prefieras, pero deberás actualizar los scripts)
   - Dimensión: 3072 (para text-embedding-3-large)
   - Métrica: cosine
   - Tipo: Serverless (recomendado para empezar)
   - Región: la más cercana a tu ubicación

### 3. Configurar variables de entorno

Edita el archivo `.env` y actualiza las siguientes variables:

```
OPENAI_API_KEY=tu-clave-de-api-de-openai
PINECONE_API_KEY=tu-clave-de-api-de-pinecone
PINECONE_ENVIRONMENT=tu-entorno-de-pinecone (por ejemplo, gcp-starter)
```

## Estructura de directorios

```
.
├── data/
│   └── renta/  # Coloca aquí tus documentos de renta (PDF, HTML, TXT)
├── ingest_renta_docs.py  # Script para ingestar documentos en Pinecone
├── query_renta_docs.py   # Script para consultar documentos desde Pinecone
└── .env                  # Archivo de variables de entorno
```

## Uso

### 1. Preparar documentos

Coloca tus documentos de renta (PDF, HTML, TXT) en el directorio `data/renta/`.

### 2. Ingestar documentos

Ejecuta el script de ingesta:

```bash
python ingest_renta_docs.py
```

Este script:
- Cargará los documentos del directorio `data/renta/`
- Los dividirá en chunks más pequeños
- Generará embeddings usando text-embedding-3-large
- Insertará los embeddings en el índice de Pinecone

### 3. Consultar documentos

Ejecuta el script de consulta:

```bash
python query_renta_docs.py
```

Este script:
- Te pedirá que ingreses una consulta sobre renta
- Buscará documentos relevantes en Pinecone
- Generará una respuesta basada en los documentos encontrados
- Mostrará la respuesta con citas a los documentos

## Personalización

Puedes modificar los siguientes parámetros en los scripts:

- `INDEX_NAME`: Nombre del índice en Pinecone
- `NAMESPACE`: Namespace dentro del índice
- `CHUNK_SIZE`: Tamaño de los chunks de texto
- `CHUNK_OVERLAP`: Superposición entre chunks
- `TOP_K`: Número de resultados a recuperar en las consultas

## Solución de problemas

### Error al crear el índice

Si encuentras errores al crear el índice, intenta crearlo manualmente desde la consola de Pinecone.

### Límites de rate en OpenAI

Si encuentras errores de límite de rate en OpenAI, puedes aumentar los tiempos de espera en las funciones `get_embeddings` y `get_embedding`.

### Documentos no encontrados

Asegúrate de que los documentos estén en el formato correcto (PDF, HTML, TXT) y en el directorio `data/renta/`.

## Recursos adicionales

- [Documentación de Pinecone](https://docs.pinecone.io/)
- [Documentación de OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Documentación de text-embedding-3-large](https://platform.openai.com/docs/models/embeddings) 

Análisis Detallado del Sistema de Recuperación de Información y Generación de Respuestas
1. Arquitectura General
El sistema implementa una arquitectura RAG (Retrieval Augmented Generation) que:
Recupera documentos relevantes basados en la consulta del usuario
Reordena los resultados para priorizar los más relevantes
Genera respuestas detalladas basadas en los documentos recuperados
Formatea las respuestas con citas y referencias a las fuentes
2. Módulo de Recuperación (retrieval.py)
Este módulo es el responsable de buscar documentos relevantes en las bases de conocimiento:
Múltiples Índices: El sistema utiliza Pinecone para almacenar vectores de incrustación (embeddings) de diferentes tipos de documentos tributarios, cada uno con su propio índice:
timbre - Documentos sobre impuesto de timbre
renta - Documentos sobre impuesto de renta
iva - Documentos sobre IVA
retencion - Documentos sobre retención en la fuente
ipoconsumo - Documentos sobre impuesto al consumo
aduanas - Documentos sobre aduanas
cambiario - Documentos sobre régimen cambiario
Clase MultiRetriever: Implementa un enrutador inteligente que selecciona la base de conocimiento adecuada según el tema de la consulta. Por ejemplo, si la consulta es sobre timbre, dirige la búsqueda al índice timbre en Pinecone.
Proceso de Búsqueda:
Convierte la consulta del usuario en un vector de embedding usando el modelo text-embedding-3-large de OpenAI
Busca en Pinecone los documentos cuyos embeddings sean más similares al de la consulta
Recupera un número predeterminado de documentos (generalmente entre 5-8, dependiendo del tema)
Convierte los resultados de Pinecone en objetos Document con metadatos (fuente, puntuación, página, etc.)
3. Módulo de Reordenamiento (reranking.py)
Este módulo mejora la calidad de los resultados mediante un reordenamiento semántico:
Función rerank_documents:
Toma la consulta original y los documentos recuperados
Utiliza GPT-4o-2024-08-06 para evaluar la relevancia de cada documento en relación con la consulta
Asigna puntuaciones de 0 a 10 a cada documento, con justificaciones
Ordena los documentos por relevancia (del más relevante al menos relevante)
Devuelve solo los K documentos más relevantes
Función retrieve_with_reranking:
Primero recupera el doble de documentos necesarios (para tener un mejor conjunto de candidatos)
Aplica el reordenamiento para filtrar los más relevantes
Devuelve solo los mejores documentos
Este enfoque en dos etapas mejora significativamente la calidad de los documentos que se utilizan para generar respuestas.
4. Módulo de Generación (openai_generation.py)
Este módulo es responsable de generar respuestas coherentes y fundamentadas:
Función format_documents_for_openai:
Formatea los documentos recuperados para incluirlos en el prompt a OpenAI
Incluye la fuente de cada documento y su contenido para que el modelo pueda citarlos correctamente
Función generate_with_openai:
Utiliza GPT-4o-2024-08-06 con un prompt extenso y detallado que:
Define el rol del asistente como experto jurídico en derecho tributario
Especifica la estructura exacta que debe seguir la respuesta (Referencia, Contenido, Entendimiento, Conclusión, Análisis)
Proporciona instrucciones sobre cómo citar los documentos usando el formato [n]
Establece directrices para enfatizar cambios normativos y controversias
Construye la respuesta completa integrando la información de los documentos con análisis crítico
Incluye citas numeradas a las fuentes utilizadas
Función extract_citations_from_text:
Analiza el texto generado para extraer las citas en formato [n]
Vincula cada número con el documento correspondiente
Extrae fragmentos representativos de cada documento citado para mostrarlos como referencias
5. Integración en las Páginas de la Aplicación
Cada página temática (como 3_Timbre.py) implementa un flujo de trabajo similar:
Inicialización:
Verifica la existencia del índice correspondiente en Pinecone
Establece el estado de la sesión para almacenar el historial de conversación
Procesamiento de Consultas:
Cuando el usuario envía una consulta, muestra un flujo de procesamiento en tiempo real
Recupera documentos relevantes usando la función especializada (ej. query_timbre)
Aplica reordenamiento con retrieve_with_reranking
Genera una respuesta con generate_with_openai
Formatea la respuesta con citas usando HTML
Visualización:
Muestra la respuesta formateada con citas numeradas
Proporciona expansores para ver:
Referencias detalladas con fragmentos de los documentos citados
Fuentes completas utilizadas con su contenido
Flujo de procesamiento que se siguió para generar la respuesta
6. Características Destacadas del Sistema
Especificidad por Dominio: Cada tipo de impuesto tiene su propio índice y parámetros optimizados.
Transparencia: El sistema muestra explícitamente las fuentes utilizadas y los fragmentos citados.
Estructura Constante: Las respuestas siguen una estructura detallada y profesional que incluye marco normativo, evolución, jurisprudencia, doctrina y consideraciones prácticas.
Sistema de Citas: Las respuestas incluyen citas numeradas que se vinculan directamente a los documentos fuente, incluyendo números de página cuando están disponibles.
Monitoreo del Proceso: El usuario puede ver el flujo de procesamiento completo, desde la recepción de la consulta hasta la generación de la respuesta.
Manejo de Errores: El sistema incluye manejo de excepciones en cada etapa para proporcionar mensajes informativos en caso de fallos.
7. Optimizaciones Importantes
Recuperación Ampliada: Se recuperan más documentos de los necesarios para permitir un mejor reordenamiento (mejora la calidad).
Limitación de Tokens: Los textos largos se truncan antes de enviarse a las APIs de OpenAI para evitar exceder límites de tokens.
Control de Temperatura: Se utiliza una temperatura baja (0.2) para la generación, lo que favorece respuestas más precisas y deterministas.
Instrucciones Detalladas: El sistema de prompting es muy específico para guiar al modelo hacia el formato y contenido deseados.
Formateo HTML: Las citas se mejoran con HTML para incluir información de página y mejorar la legibilidad.
Este sistema representa una implementación avanzada de RAG para un dominio especializado, con optimizaciones específicas para mejorar la calidad, relevancia y fundamentación de las respuestas generadas.