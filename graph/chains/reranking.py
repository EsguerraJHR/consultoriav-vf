"""
Módulo para implementar reranking de documentos recuperados.
Esto mejora la relevancia de los documentos antes de generar respuestas.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.documents import Document

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def rerank_documents(query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
    """
    Reordena los documentos según su relevancia para la consulta utilizando OpenAI.
    
    Args:
        query: La consulta del usuario
        documents: Lista de documentos recuperados
        top_k: Número de documentos a devolver después del reranking
        
    Returns:
        Lista reordenada de documentos más relevantes
    """
    if not documents:
        return []
    
    if len(documents) <= top_k:
        return documents
    
    print(f"Reranking {len(documents)} documentos...")
    
    # Preparar los documentos para evaluación
    doc_texts = []
    for i, doc in enumerate(documents):
        # Limitar el tamaño del texto para evitar tokens excesivos
        text = doc.page_content[:1000] + "..." if len(doc.page_content) > 1000 else doc.page_content
        doc_texts.append(f"Documento {i+1}:\n{text}")
    
    # Crear el prompt para evaluar la relevancia
    system_message = """Eres un experto en derecho tributario colombiano. Tu tarea es evaluar la relevancia de varios documentos para responder a una consulta específica.
    
Para cada documento, asigna una puntuación de relevancia del 0 al 10, donde:
- 0: Completamente irrelevante
- 5: Parcialmente relevante
- 10: Extremadamente relevante y responde directamente a la consulta

Proporciona tu evaluación en formato JSON con la siguiente estructura:
{
  "evaluaciones": [
    {"documento": 1, "puntuacion": X, "justificacion": "Breve explicación"},
    {"documento": 2, "puntuacion": Y, "justificacion": "Breve explicación"},
    ...
  ]
}"""
    
    user_message = "Consulta: " + query + "\n\nDocumentos a evaluar:\n" + "\n\n".join(doc_texts) + "\n\nEvalúa la relevancia de cada documento para responder a la consulta. Proporciona tu evaluación en formato JSON."
    
    try:
        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Extraer las evaluaciones
        result = response.choices[0].message.content
        import json
        evaluations = json.loads(result)
        
        # Ordenar los documentos según las puntuaciones
        scored_docs = []
        for eval_item in evaluations.get("evaluaciones", []):
            doc_index = eval_item.get("documento", 0) - 1
            if 0 <= doc_index < len(documents):
                scored_docs.append({
                    "document": documents[doc_index],
                    "score": eval_item.get("puntuacion", 0),
                    "justification": eval_item.get("justificacion", "")
                })
        
        # Ordenar por puntuación (de mayor a menor)
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        
        # Imprimir información sobre el reranking
        print("Resultados del reranking:")
        for i, item in enumerate(scored_docs[:top_k]):
            source = item["document"].metadata.get("source", "Desconocido")
            print(f"  {i+1}. Puntuación: {item['score']}/10 - Fuente: {source}")
            print(f"     Justificación: {item['justification']}")
        
        # Devolver los documentos reordenados
        return [item["document"] for item in scored_docs[:top_k]]
    
    except Exception as e:
        print(f"Error en el reranking: {str(e)}")
        # En caso de error, devolver los documentos originales
        return documents[:top_k]

# Función para integrar el reranking en el flujo de recuperación
def retrieve_with_reranking(query: str, retriever_func, top_k: int = 5, **kwargs):
    """
    Recupera documentos y aplica reranking para mejorar la relevancia.
    
    Args:
        query: La consulta del usuario
        retriever_func: Función de recuperación a utilizar
        top_k: Número de documentos a devolver después del reranking
        **kwargs: Argumentos adicionales para la función de recuperación
        
    Returns:
        Lista de documentos más relevantes después del reranking
    """
    # Recuperar más documentos de los necesarios para tener un mejor pool para reranking
    initial_docs = retriever_func(query, top_k=top_k*2, **kwargs)
    
    # Aplicar reranking
    reranked_docs = rerank_documents(query, initial_docs, top_k=top_k)
    
    return reranked_docs 

def retrieve_with_multi_index_reranking(query: str, top_k: int = 10):
    """
    Recupera documentos de múltiples índices y aplica reranking global.
    
    Esta función recupera documentos de todos los índices disponibles,
    luego aplica reranking para obtener los más relevantes independientemente
    de su origen.
    
    Args:
        query: La consulta del usuario
        top_k: Número de documentos a devolver después del reranking
        
    Returns:
        Lista de documentos más relevantes después del reranking
    """
    # Importar aquí para evitar dependencias circulares
    from graph.chains.retrieval import query_all_indices
    
    print(f"retrieve_with_multi_index_reranking: Consultando múltiples índices para: '{query}'")
    
    # Recuperar documentos de todos los índices (más de los necesarios)
    initial_docs = query_all_indices(query, top_k=top_k*2)
    
    print(f"retrieve_with_multi_index_reranking: Recuperados {len(initial_docs)} documentos en total")
    
    if not initial_docs:
        print("No se encontraron documentos en ningún índice")
        return []
    
    # Aplicar reranking a todos los documentos combinados
    print(f"retrieve_with_multi_index_reranking: Aplicando reranking global...")
    reranked_docs = rerank_documents(query, initial_docs, top_k=top_k)
    
    # Imprimir información sobre el origen de los documentos reordenados
    indices_counts = {}
    for doc in reranked_docs:
        index_name = doc.metadata.get('source_index', 'Desconocido')
        if index_name in indices_counts:
            indices_counts[index_name] += 1
        else:
            indices_counts[index_name] = 1
    
    print(f"retrieve_with_multi_index_reranking: Distribución final de documentos por índice:")
    for index_name, count in indices_counts.items():
        print(f"  - {index_name}: {count} documentos")
    
    return reranked_docs 