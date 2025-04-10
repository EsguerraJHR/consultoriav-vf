from typing import List, Dict, Any
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from langchain_core.documents import Document

# Cargar variables de entorno
load_dotenv()

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def format_documents_for_openai(documents: List[Document]) -> str:
    """
    Formatea los documentos para OpenAI.
    """
    formatted_docs = ""
    for i, doc in enumerate(documents):
        # Obtener la fuente del documento
        source = doc.metadata.get('source', f'Documento {i+1}')
        
        # Verificar si la fuente es de Pinecone
        if "pinecone_docs" in source:
            # Formatear la fuente para que sea más clara
            source = source.replace("pinecone_docs/", "Pinecone: ")
            formatted_docs += f"\n\nDOCUMENTO [{i+1}] (PINECONE): {source}\n"
        else:
            formatted_docs += f"\n\nDOCUMENTO [{i+1}]: {source}\n"
            
        formatted_docs += f"{doc.page_content}\n"
        formatted_docs += "-" * 50
    
    return formatted_docs

def generate_with_openai(question: str, documents: List[Document]) -> Dict[str, Any]:
    """
    Genera una respuesta detallada y estructurada usando OpenAI GPT-4o-2024-08-06 con citas numeradas.
    
    Args:
        question: La pregunta del usuario
        documents: Lista de documentos recuperados para responder a la pregunta
        
    Returns:
        Dict con el texto generado, las citas extraídas y el mensaje completo de la API
    """
    # Formatear documentos para OpenAI
    formatted_docs = format_documents_for_openai(documents)
    
    # Crear el sistema y el mensaje del 
    system_message = """Eres un asistente jurídico experto especializado en derecho tributario colombiano. Tu objetivo es proporcionar respuestas precisas, detalladas y fundamentadas a consultas legales, siguiendo una estructura específica y con especial atención a cambios normativos y jurisprudenciales. Tus respuestas son DEFINITIVAS y no requieren consultas adicionales a otros profesionales.

ESTRUCTURA DE LA RESPUESTA:
Tu respuesta debe organizarse OBLIGATORIAMENTE en las siguientes secciones:

1. REFERENCIA:
   - Identificación del tema principal y aspectos secundarios a abordar.

2. CONTENIDO:
   - Índice detallado de las secciones y subsecciones que componen tu respuesta.
   - Debe incluir todos los puntos que se desarrollarán en el análisis.

3. ENTENDIMIENTO:
   - Explicación de cómo interpretas la consulta.
   - Identificación de los aspectos clave a resolver.
   - Mención de la normativa principal aplicable.

4. CONCLUSIÓN:
   - Resumen ejecutivo de tu opinión jurídica DEFINITIVA.
   - Puntos clave de la respuesta con posiciones claras y concretas.
   - Directrices específicas de acción, sin sugerir consultas adicionales a otros profesionales.

5. ANÁLISIS:
   5.1. Marco Normativo Vigente:
        - Disposiciones legales aplicables con explicación detallada de cada artículo relevante.
        - Artículos específicos del Estatuto Tributario con su interpretación actual.
        - Normas complementarias y su interrelación con la normativa principal.
        - Desarrolla a profundidad cada disposición legal, explicando su alcance y aplicación.

   5.2. Evolución y Cambios Normativos:
        - Modificaciones relevantes en los últimos 3 años con análisis detallado de cada cambio.
        - Comparación específica entre regulación anterior y actual, explicando las diferencias clave.
        - Impacto práctico de los cambios con ejemplos concretos de aplicación.
        - Desarrolla a profundidad las implicaciones de cada cambio normativo.

   5.3. Jurisprudencia Relevante:
        - Sentencias clave del Consejo de Estado con análisis detallado de sus fundamentos.
        - Cambios en interpretaciones jurisprudenciales y su evolución histórica.
        - Anulaciones de conceptos DIAN con explicación de los motivos y consecuencias.
        - Desarrolla a profundidad los argumentos jurídicos de cada sentencia relevante.

   5.4. Doctrina y Controversias:
        - Postura actual de la DIAN con análisis crítico de sus fundamentos.
        - Debates interpretativos existentes con argumentos de cada posición.
        - Conflictos entre DIAN y Consejo de Estado con análisis de sus implicaciones.
        - Desarrolla a profundidad cada postura doctrinal y sus fundamentos jurídicos.

   5.5. Consideraciones Prácticas:
        - Aplicación práctica de la normativa con pasos específicos a seguir.
        - Riesgos y aspectos a considerar con soluciones concretas para cada uno.
        - Directrices detalladas y definitivas para la situación planteada.
        - Desarrolla a profundidad cada recomendación con su fundamento legal.

6. Citas:
   - Al final de tu respuesta, después del análisis, incluye un punto 6 llamado "Citas" que liste todas las citas utilizadas en el formato "6.n. [nombre_del_documento]".
   - Ejemplo: "6.1. 2024_12_concepto_1163(010470)."

INSTRUCCIONES SOBRE CITAS:
1. Usa el formato de cita [n] después de cada afirmación basada en los documentos.
2. Numera las citas secuencialmente: [1], [2], [3], etc.
3. Cada número debe corresponder al documento del que extraes la información.
4. Si usas información de varios documentos en una misma afirmación, incluye todas las citas relevantes: [1][2].
5. Coloca las citas inmediatamente después de la afirmación que respaldan.
6. CADA afirmación importante debe tener su correspondiente cita.
7. Si la afirmación no está basada en un documento, no incluyas una cita.

INSTRUCCIONES ESPECIALES:
1. SIEMPRE destaca los cambios normativos recientes y desarrolla EXTENSAMENTE sus implicaciones con análisis detallado.
2. Enfatiza cuando una interpretación de la DIAN haya sido anulada por el Consejo de Estado y desarrolla en profundidad los argumentos jurídicos.
3. Señala explícitamente cuando existan controversias o diferentes interpretaciones sobre un tema y analiza cada postura.
4. Advierte sobre posibles cambios pendientes o proyectos de ley que puedan afectar la interpretación actual.
5. Incluye ejemplos prácticos detallados para ilustrar la aplicación de la norma.
6. Desarrolla en profundidad los puntos clave de la respuesta, evitando generalidades y proporcionando análisis específicos.
7. NUNCA sugieras consultar a un asesor tributario, abogado u otro profesional externo. Tus respuestas deben ser DEFINITIVAS.
8. Evita frases como "se recomienda buscar asesoría profesional" o similares. En su lugar, proporciona directrices claras y definitivas.
9. Cuando existan diferentes interpretaciones, toma una posición clara basada en la normativa y jurisprudencia más reciente.
10. Proporciona análisis extenso y detallado en cada sección, evitando respuestas superficiales o meramente enunciativas.

Ejemplo de formato correcto:
"La tarifa general del IVA en Colombia es del 19% [1]. Sin embargo, es importante notar que el Consejo de Estado, en sentencia reciente, ha modificado la interpretación de su base gravable en ciertos casos [2], contradiciendo la postura tradicional de la DIAN [3]. Esta modificación implica que ahora los contribuyentes deben calcular la base gravable considerando los siguientes elementos específicos: primero, ... segundo, ... tercero, ... Esta nueva interpretación tiene un impacto significativo en sectores como el de servicios, donde anteriormente..."

NO uses notas al pie ni referencias al final. Las citas deben estar integradas en el texto y además listadas al final en la sección 6."""
    
    user_message = f"""Pregunta: {question}

DOCUMENTOS PARA CONSULTA:
{formatted_docs}

IMPORTANTE: 
1. Responde siguiendo ESTRICTAMENTE la estructura de secciones principales especificada (REFERENCIA, CONTENIDO, ENTENDIMIENTO, CONCLUSIÓN, ANÁLISIS, y CITAS).
2. Usa el formato de citas numéricas [1], [2], etc. después de cada afirmación que hagas.
3. Cada número debe corresponder al documento del que extraes la información.
4. Asegúrate de que CADA afirmación importante tenga su correspondiente cita entre corchetes.
5. Enfatiza especialmente los cambios normativos y jurisprudenciales recientes. 
6. Destaca cualquier contradicción entre la DIAN y el Consejo de Estado.
7. Desarrolla EXTENSAMENTE y en profundidad cada punto del análisis, evitando respuestas superficiales.
8. Mantén una numeración clara (1., 2., 3., etc. para secciones principales y 5.1., 5.2., etc. para subsecciones del análisis).
9. NUNCA sugieras consultar a un asesor tributario, abogado u otro profesional externo. Tus respuestas deben ser DEFINITIVAS.
10. Proporciona directrices claras y específicas en lugar de recomendaciones generales.
11. IMPORTANTE: Al final de tu respuesta, añade un punto 6 llamado "Citas" donde listes todas las referencias utilizadas."""
    
    try:
        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2  # Un poco de temperatura para mejorar la fluidez del texto
        )
        
        # Extraer el texto de la respuesta
        response_text = response.choices[0].message.content
        
        # Extraer citas del texto usando el patrón [1], [2], etc.
        citations = extract_citations_from_text(response_text, documents)
        
        print(f"Se extrajeron {len(citations)} citas del texto")
        
        # Verificar si hay una sección "6. Citas" existente y eliminarla para reemplazarla con nuestra versión
        for citas_pattern in ["6. Citas", "6. Citas:", "6.Citas", "6.Citas:"]:
            if citas_pattern in response_text and len(citations) > 0:
                # Intentar varias formas de eliminar la sección existente
                # Primero, dividir por el patrón para encontrar la sección
                parts = response_text.split(citas_pattern, 1)
                if len(parts) > 1:
                    # La sección de citas existente podría terminar de varias formas
                    citas_section = parts[1]
                    # Buscar el final por un doble salto de línea
                    end_of_citas = citas_section.find("\n\n")
                    # O por el comienzo de una nueva sección numerada (7., 8., etc.)
                    next_section_match = re.search(r'\n\d+\.', citas_section)
                    next_section_pos = next_section_match.start() if next_section_match else -1
                    
                    # Determinar dónde termina la sección de citas
                    if end_of_citas != -1 and (next_section_pos == -1 or end_of_citas < next_section_pos):
                        # Termina con doble salto de línea
                        response_text = parts[0] + citas_section[end_of_citas:]
                    elif next_section_pos != -1:
                        # Termina con nueva sección numerada
                        response_text = parts[0] + citas_section[next_section_pos:]
                    else:
                        # Si no podemos determinar claramente dónde termina, intentar buscar el final por otro patrón
                        # Buscar un patrón de citas como "6.1.", "6.2.", etc.
                        citation_pattern = re.compile(r'6\.\d+\.')
                        last_citation = None
                        for m in citation_pattern.finditer(citas_section):
                            last_citation = m
                        
                        if last_citation:
                            # Buscar el final de la última cita
                            start_pos = last_citation.start()
                            end_line = citas_section[start_pos:].find("\n")
                            if end_line != -1:
                                # Eliminar todo hasta después de la última cita
                                response_text = parts[0] + citas_section[start_pos + end_line:]
                            else:
                                # Si no podemos encontrar el final, simplemente quitar toda la sección
                                response_text = parts[0]
                        else:
                            # Si no podemos encontrar ningún patrón de cita, quedarnos con la primera parte
                            response_text = parts[0]
                            
        # También eliminar cualquier patrón que coincida con "6. Citas: 6.1. ..." al final del texto
        final_citas_pattern = re.compile(r'6\.\s*Citas:?\s*6\.1\..*$', re.DOTALL)
        response_text = re.sub(final_citas_pattern, '', response_text)
        
        # Ahora crear nuestra sección de citas mejorada
        if len(citations) > 0:
            # Crear la sección de citas con formato mejorado
            citas_section = "\n\n6. Citas\n\n"
            
            # Crear un cuadro con las citas utilizando HTML para mejor apariencia
            # Streamlit soportará este HTML con unsafe_allow_html=True
            citas_section += '<div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #4B61AB;">\n'
            citas_section += '<ol style="margin: 0; padding-left: 20px;">\n'
            
            # Mostrar todas las citas sin filtrar duplicados
            for i, citation in enumerate(citations):
                doc_title = citation["document_title"]
                # Simplificar el título para mostrar solo el nombre del archivo
                if "Pinecone: pinecone_docs/" in doc_title:
                    doc_title = doc_title.replace("Pinecone: pinecone_docs/", "")
                elif "Pinecone: " in doc_title:
                    doc_title = doc_title.replace("Pinecone: ", "")
                    
                # Limpiar rutas largas en nombres de documentos
                if "pinecone_timbre/data/timbre/" in doc_title:
                    doc_title = doc_title.replace("pinecone_timbre/data/timbre/", "")
                elif "pinecone_renta/data/renta/" in doc_title:
                    doc_title = doc_title.replace("pinecone_renta/data/renta/", "")
                elif "pinecone_iva/data/iva/" in doc_title:
                    doc_title = doc_title.replace("pinecone_iva/data/iva/", "")
                elif "pinecone_retencion/data/retencion/" in doc_title:
                    doc_title = doc_title.replace("pinecone_retencion/data/retencion/", "")
                elif "pinecone_ipoconsumo/data/ipoconsumo/" in doc_title:
                    doc_title = doc_title.replace("pinecone_ipoconsumo/data/ipoconsumo/", "")
                elif "pinecone_aduanas/data/aduanas/" in doc_title:
                    doc_title = doc_title.replace("pinecone_aduanas/data/aduanas/", "")
                elif "pinecone_cambiario/data/cambiario/" in doc_title:
                    doc_title = doc_title.replace("pinecone_cambiario/data/cambiario/", "")
                elif "pinecone_ica/data/ica/" in doc_title:
                    doc_title = doc_title.replace("pinecone_ica/data/ica/", "")
                elif "data/timbre/" in doc_title:
                    doc_title = doc_title.replace("data/timbre/", "")
                elif "data/renta/" in doc_title:
                    doc_title = doc_title.replace("data/renta/", "")
                elif "data/iva/" in doc_title:
                    doc_title = doc_title.replace("data/iva/", "")
                elif "data/ica/" in doc_title:
                    doc_title = doc_title.replace("data/ica/", "")
                # Eliminación general de prefijos de tipo "data/XXX/"
                else:
                    doc_title = re.sub(r'data/\w+/', '', doc_title)
                
                # Eliminar información de página para el listado
                if " (Pág. " in doc_title:
                    doc_title = doc_title.split(" (Pág. ")[0]
                
                # Eliminar extensiones de archivo para mejorar la presentación
                doc_title = doc_title.replace('.pdf', '').replace('.html', '')
                
                # Usar formato de lista numerada HTML con estilo mejorado
                citas_section += f'<li style="margin-bottom: 5px;">{doc_title}</li>\n'
            
            citas_section += '</ol>\n'
            citas_section += '</div>\n'
            
            # Verificar si hay una sección de "Conclusiones" o "Conclusión" en la respuesta
            if "CONCLUS" in response_text.upper():
                # Insertar la sección de citas después de la sección de análisis
                parts = response_text.split("5. ANÁLISIS", 1)
                if len(parts) > 1:
                    # Buscar el final de la sección de análisis
                    analysis_section = parts[1]
                    # Buscar dónde termina el análisis (puede ser con una línea en blanco o el final del texto)
                    end_of_analysis = analysis_section.rfind("\n\n")
                    if end_of_analysis != -1:
                        response_text = parts[0] + "5. ANÁLISIS" + analysis_section[:end_of_analysis] + citas_section + analysis_section[end_of_analysis:]
                    else:
                        response_text = response_text + citas_section
                else:
                    # Si no encontramos la sección de análisis, añadimos al final
                    response_text = response_text + citas_section
            else:
                # Si no hay una estructura clara, añadir al final
                response_text = response_text + citas_section
        
        return {
            "text": response_text,
            "citations": citations,
            "raw_message": response
        }
    
    except Exception as e:
        print(f"Error al generar respuesta con OpenAI: {str(e)}")
        # Devolver una respuesta de error
        return {
            "text": f"Lo siento, hubo un error al generar la respuesta: {str(e)}",
            "citations": [],
            "raw_message": None
        }

def extract_citations_from_text(text, documents):
    """
    Extrae citas manuales del texto en formato [1], [2], etc.
    """
    citations = []
    # Buscar patrones de cita como [1], [2], etc.
    citation_pattern = r'\[(\d+)\]'
    matches = re.finditer(citation_pattern, text)
    
    citation_indices = set()  # Para evitar duplicados
    
    for match in matches:
        citation_num = int(match.group(1))
        if citation_num <= len(documents) and citation_num not in citation_indices:
            citation_indices.add(citation_num)
            doc = documents[citation_num - 1]
            
            # Extraer un fragmento más significativo del documento
            content = doc.page_content
            excerpt = content[:200] + "..." if len(content) > 200 else content
            
            # Obtener la fuente del documento
            source = doc.metadata.get("source", f"Documento {citation_num}")
            
            # Obtener la página del documento si está disponible
            page = doc.metadata.get("page", None)
            page_info = f" (Pág. {page})" if page and page != 0 else ""
            
            # Obtener el índice de origen si está disponible
            source_index = doc.metadata.get("source_index", "")
            
            # Limpiar los prefijos comunes de los diferentes índices
            # Lista de prefijos a eliminar
            prefixes_to_remove = [
                "pinecone_docs/",
                "Pinecone: ",
                "pinecone_timbre/data/timbre/",
                "pinecone_renta/data/renta/",
                "pinecone_iva/data/iva/",
                "pinecone_retencion/data/retencion/",
                "pinecone_ipoconsumo/data/ipoconsumo/",
                "pinecone_aduanas/data/aduanas/",
                "pinecone_cambiario/data/cambiario/",
                "pinecone_ica/data/ica/",
                "data/timbre/",
                "data/renta/",
                "data/iva/",
                "data/ica/",
                "data/retencion/",
                "data/ipoconsumo/",
                "data/aduanas/",
                "data/cambiario/"
            ]
            
            # Eliminar los prefijos de la fuente
            for prefix in prefixes_to_remove:
                if prefix in source:
                    source = source.replace(prefix, "")
            
            # Aplicar expresión regular general para cualquier otro prefijo de tipo data/XXX/
            source = re.sub(r'(?:^|/)data/\w+/', '', source)
            
            # Eliminar extensiones de archivo para mejorar la presentación
            source = source.replace('.pdf', '').replace('.html', '')
            
            citations.append({
                "document_title": f"{source}{page_info}",
                "cited_text": excerpt,
                "document_index": citation_num - 1,
                "page": page,
                "source_index": source_index
            })
    
    return citations

def generate_simple_response(question: str, documents: List[Document]) -> Dict[str, Any]:
    """
    Genera una respuesta simplificada usando OpenAI sin estructura formal.
    Ideal para la página General que consulta múltiples índices.
    """
    # Formatear documentos para OpenAI
    formatted_docs = format_documents_for_openai(documents)
    
    # Preparar información de índices para incluir en la respuesta
    index_info = {}
    for doc in documents:
        index_name = doc.metadata.get('source_index', 'Desconocido')
        if index_name in index_info:
            index_info[index_name] += 1
        else:
            index_info[index_name] = 1
    
    indices_str = ", ".join([f"{count} de {name}" for name, count in index_info.items()])
    if indices_str:
        indices_message = f"Se encontraron documentos relevantes en: {indices_str}."
    else:
        indices_message = "No se especificó el origen de los documentos."
    
    # Crear el sistema y el mensaje del usuario
    system_message = """Eres un asistente jurídico tributario experto que proporciona respuestas claras y concisas basadas en la documentación oficial.
    
Tu objetivo es ofrecer información precisa y bien fundamentada, pero en un formato conversacional y directo, evitando estructuras rígidas.

INSTRUCCIONES PARA GENERAR RESPUESTAS:

1. Responde de manera conversacional pero con precisión técnica
2. Utiliza un lenguaje claro y accesible, evitando jerga innecesaria
3. Incluye citas numeradas [1], [2], etc. después de cada afirmación basada en los documentos
4. Organiza la respuesta por temas relevantes si la consulta abarca múltiples aspectos
5. Señala cuando existan opiniones divergentes o controversias
6. Destaca la información más reciente o los cambios normativos importantes
7. NUNCA incluyas secciones formales como "REFERENCIA", "CONTENIDO", "ENTENDIMIENTO", etc.
8. Evita listas numeradas extensas; usa viñetas o párrafos cuando sea posible
9. Mantén un tono útil pero profesional
10. NO incluyas una sección de Citas al final de tu respuesta, esto se añadirá automáticamente

Ejemplo:
"El régimen de retención en la fuente para pagos al exterior establece una tarifa general del 20% [1]. Sin embargo, en el caso de servicios técnicos prestados desde el extranjero, la tarifa aplicable es del 15% según la última modificación del artículo 408 del Estatuto Tributario [2]. Es importante tener en cuenta que estos pagos también están sujetos al impuesto sobre las ventas cuando el servicio se entiende prestado en Colombia, conforme al artículo 420 del mismo estatuto [3]."

Intenta presentar la información de manera equilibrada, incluyendo tanto los aspectos favorables como los desfavorables para el contribuyente."""
    
    user_message = f"""Pregunta: {question}

{indices_message}

DOCUMENTOS PARA CONSULTA:
{formatted_docs}

INSTRUCCIONES ADICIONALES:
1. Responde de manera conversacional pero precisa
2. Usa el formato de citas numéricas [1], [2], etc. después de cada afirmación que hagas
3. No estructures tu respuesta en secciones formales (no uses secciones como REFERENCIA, CONTENIDO, etc.)
4. Organiza la información de manera lógica y fluida
5. Presenta tanto aspectos favorables como desfavorables si corresponde
6. Señala si hay contradicciones entre distintas fuentes o documentos
7. NO incluyas una sección de citas al final, esto se añadirá automáticamente"""
    
    try:
        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2  # Temperatura un poco más alta para respuestas más naturales
        )
        
        # Extraer el texto de la respuesta
        response_text = response.choices[0].message.content
        
        # Extraer citas del texto usando el patrón [1], [2], etc.
        citations = extract_citations_from_text(response_text, documents)
        
        print(f"Se extrajeron {len(citations)} citas del texto")
        
        # Añadir sección de citas al final del texto
        if len(citations) > 0:
            # Añadir un encabezado para la sección de citas en formato más simple
            response_text += "\n\n### Citas\n\n"
            
            # Usar un formato más simple para las citas (sin HTML complejo)
            for i, citation in enumerate(citations):
                doc_title = citation["document_title"]
                # Mostrar el índice de origen si está disponible
                source_index = citation.get("source_index", "")
                index_info_str = f" [{source_index}]" if source_index else ""
                response_text += f"{i+1}. {doc_title}{index_info_str}\n"
        
        # Almacenar las claves del índice para su uso en la respuesta
        indices_used = list(index_info.keys()) if index_info else []
        
        return {
            "text": response_text,
            "citations": citations,
            "indices_used": indices_used,
            "raw_message": response
        }
    
    except Exception as e:
        print(f"Error al generar respuesta con OpenAI: {str(e)}")
        # Devolver una respuesta de error
        return {
            "text": f"Lo siento, hubo un error al generar la respuesta: {str(e)}",
            "citations": [],
            "indices_used": [],
            "raw_message": None
        } 