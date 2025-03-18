import os
from typing import List
from dotenv import load_dotenv
import pinecone
from openai import OpenAI
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Cargar variables de entorno
load_dotenv()

# Configuración para Chroma (IVA)
chroma_retriever = Chroma(
    collection_name="legal-docs-chroma",
    persist_directory="./.chroma",
    embedding_function=OpenAIEmbeddings(),
).as_retriever()

# Configuración para Pinecone (común)
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT", "us-east-1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-large"
TOP_K = 5  # Número de resultados a recuperar

# Configuración específica para Renta
RENTA_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "ejhr")
RENTA_NAMESPACE = "renta"

# Configuración específica para Timbre
TIMBRE_INDEX_NAME = "timbre"
TIMBRE_NAMESPACE = "timbre"
TIMBRE_TOP_K = 8  # Valor específico para Timbre

# Configuración específica para Dian Full
DIANFULL_INDEX_NAME = "dianfull"
DIANFULL_NAMESPACE = "dianfull"

# Configuración específica para Retención
RETENCION_INDEX_NAME = "retencion"
RETENCION_NAMESPACE = "retencion"
RETENCION_TOP_K = 8  # Valor aumentado específicamente para Retención

# Configuración específica para IVA
IVA_INDEX_NAME = "iva"
IVA_NAMESPACE = "iva"
IVA_TOP_K = 8  # Valor específico para IVA

# Configuración específica para Impuesto al Consumo
IPOCONSUMO_INDEX_NAME = "ipoconsumo"
IPOCONSUMO_NAMESPACE = "ipoconsumo"
IPOCONSUMO_TOP_K = 8  # Valor específico para Impuesto al Consumo

# Configuración específica para Aduanas
ADUANAS_INDEX_NAME = "aduanas"
ADUANAS_NAMESPACE = "aduanas"
ADUANAS_TOP_K = 8  # Valor específico para Aduanas

# Configuración específica para Cambiario
CAMBIARIO_INDEX_NAME = "cambiario"
CAMBIARIO_NAMESPACE = "cambiario"
CAMBIARIO_TOP_K = 8  # Valor específico para Cambiario

# Inicializar cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str) -> List[float]:
    """
    Obtiene el embedding para un texto usando OpenAI.
    """
    response = client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def initialize_pinecone(index_name):
    """
    Inicializa la conexión con Pinecone para un índice específico.
    """
    try:
        print(f"initialize_pinecone: Inicializando Pinecone con API_KEY={PINECONE_API_KEY[:4]}... y ENVIRONMENT={PINECONE_ENVIRONMENT}")
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # Verificar si el índice existe
        existing_indexes = [index.name for index in pc.list_indexes()]
        print(f"initialize_pinecone: Índices existentes: {existing_indexes}")
        
        if index_name not in existing_indexes:
            print(f"initialize_pinecone: El índice {index_name} no existe.")
            return None
        
        print(f"initialize_pinecone: Conectando al índice {index_name}")
        return pc.Index(index_name)
    except Exception as e:
        print(f"Error al inicializar Pinecone: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def query_pinecone(query: str, index_name=RENTA_INDEX_NAME, namespace=RENTA_NAMESPACE, top_k: int = TOP_K):
    """
    Consulta Pinecone para obtener documentos relevantes.
    """
    print(f"query_pinecone: Consultando Pinecone para: '{query}' en índice {index_name}, namespace {namespace}")
    # Inicializar Pinecone
    index = initialize_pinecone(index_name)
    if not index:
        print(f"query_pinecone: No se pudo inicializar Pinecone para el índice {index_name}")
        return []
    
    try:
        # Obtener embedding para la consulta
        print("query_pinecone: Obteniendo embedding para la consulta")
        query_embedding = get_embedding(query)
        
        # Consultar Pinecone
        print(f"query_pinecone: Consultando índice {index_name}, namespace '{namespace}'")
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True
        )
        
        print(f"query_pinecone: Resultados obtenidos: {len(results.matches)}")
        
        # Imprimir información sobre los resultados
        for i, match in enumerate(results.matches):
            print(f"  Resultado {i+1}: score={match.score}, source={match.metadata.get('source', 'N/A')}")
        
        # Convertir resultados a documentos de Langchain
        documents = []
        for i, match in enumerate(results.matches):
            # Crear una fuente que sea claramente de Pinecone
            original_source = match.metadata.get('source', f'Documento-Pinecone-{i+1}')
            
            # Determinar el prefijo según el namespace
            if namespace == RENTA_NAMESPACE:
                prefix = "pinecone_renta"
            elif namespace == TIMBRE_NAMESPACE:
                prefix = "pinecone_timbre"
            elif namespace == DIANFULL_NAMESPACE:
                prefix = "pinecone_dianfull"
            else:
                prefix = "pinecone_docs"
                
            # Reemplazar cualquier referencia a legal_docs con el prefijo correspondiente
            if 'legal_docs' in original_source:
                source = original_source.replace('legal_docs', prefix)
            else:
                source = f"{prefix}/{original_source}"
                
            doc = Document(
                page_content=match.metadata.get('text', ''),
                metadata={
                    'source': source,
                    'score': match.score,
                    'page': match.metadata.get('page', 0)
                }
            )
            documents.append(doc)
        
        print(f"query_pinecone: Documentos convertidos: {len(documents)}")
        return documents
    except Exception as e:
        print(f"Error al consultar Pinecone: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def query_timbre(query: str, top_k: int = TIMBRE_TOP_K):
    """
    Consulta específica para documentos de Timbre.
    """
    return query_pinecone(query, index_name=TIMBRE_INDEX_NAME, namespace=TIMBRE_NAMESPACE, top_k=top_k)

def query_dianfull(query: str, top_k: int = TOP_K):
    """
    Consulta específica para documentos de Dian Full.
    """
    return query_pinecone(query, index_name=DIANFULL_INDEX_NAME, namespace=DIANFULL_NAMESPACE, top_k=top_k)

def query_retencion(query: str, top_k: int = RETENCION_TOP_K):
    """
    Consulta específica para documentos de Retención.
    """
    return query_pinecone(query, index_name=RETENCION_INDEX_NAME, namespace=RETENCION_NAMESPACE, top_k=top_k)

def query_iva(query: str, top_k: int = IVA_TOP_K):
    """
    Consulta específica para documentos de IVA.
    """
    return query_pinecone(query, index_name=IVA_INDEX_NAME, namespace=IVA_NAMESPACE, top_k=top_k)

def query_ipoconsumo(query: str, top_k: int = IPOCONSUMO_TOP_K):
    """
    Consulta específica para documentos de Impuesto al Consumo.
    """
    return query_pinecone(query, index_name=IPOCONSUMO_INDEX_NAME, namespace=IPOCONSUMO_NAMESPACE, top_k=top_k)

def query_aduanas(query: str, top_k: int = ADUANAS_TOP_K):
    """
    Consulta específica para documentos de Aduanas.
    """
    return query_pinecone(query, index_name=ADUANAS_INDEX_NAME, namespace=ADUANAS_NAMESPACE, top_k=top_k)

def query_cambiario(query: str, top_k: int = CAMBIARIO_TOP_K):
    """
    Consulta específica para documentos de Cambiario.
    """
    return query_pinecone(query, index_name=CAMBIARIO_INDEX_NAME, namespace=CAMBIARIO_NAMESPACE, top_k=top_k)

class MultiRetriever:
    """
    Retriever que puede consultar diferentes fuentes según el tema.
    """
    def invoke(self, query: str, topic: str = None):
        """
        Invoca el retriever adecuado según el tema.
        """
        print(f"MultiRetriever: Tema seleccionado = '{topic}'")
        
        # Asegurarnos de que topic es una cadena y hacer una comparación exacta
        if topic is not None:
            if topic.strip() == "Renta":
                # Usar Pinecone para consultas de Renta
                print("MultiRetriever: Usando Pinecone para consultas de Renta")
                docs = query_pinecone(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (Renta)")
                return docs
            elif topic.strip() == "Timbre":
                # Usar Pinecone para consultas de Timbre
                print("MultiRetriever: Usando Pinecone para consultas de Timbre")
                docs = query_timbre(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (Timbre)")
                return docs
            elif topic.strip() == "Dian Full":
                # Usar Pinecone para consultas de Dian Full
                print("MultiRetriever: Usando Pinecone para consultas de Dian Full")
                docs = query_dianfull(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (Dian Full)")
                return docs
            elif topic.strip() == "Retención":
                # Usar Pinecone para consultas de Retención
                print("MultiRetriever: Usando Pinecone para consultas de Retención")
                docs = query_retencion(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (Retención)")
                return docs
            elif topic.strip() == "IVA":
                # Usar Pinecone para consultas de IVA
                print("MultiRetriever: Usando Pinecone para consultas de IVA")
                docs = query_iva(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (IVA)")
                return docs
            elif topic.strip() == "Impuesto al Consumo":
                # Usar Pinecone para consultas de Impuesto al Consumo
                print("MultiRetriever: Usando Pinecone para consultas de Impuesto al Consumo")
                docs = query_ipoconsumo(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (Impuesto al Consumo)")
                return docs
            elif topic.strip() == "Aduanas":
                # Usar Pinecone para consultas de Aduanas
                print("MultiRetriever: Usando Pinecone para consultas de Aduanas")
                docs = query_aduanas(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (Aduanas)")
                return docs
            elif topic.strip() == "Cambiario":
                # Usar Pinecone para consultas de Cambiario
                print("MultiRetriever: Usando Pinecone para consultas de Cambiario")
                docs = query_cambiario(query)
                print(f"MultiRetriever: Recuperados {len(docs)} documentos de Pinecone (Cambiario)")
                return docs
        
        # Usar Chroma para otros temas (por defecto IVA)
        print(f"MultiRetriever: Usando Chroma para consultas de '{topic if topic else 'IVA'}'")
        docs = chroma_retriever.invoke(query)
        print(f"MultiRetriever: Recuperados {len(docs)} documentos de Chroma")
        return docs

# Crear una instancia del MultiRetriever
retriever = MultiRetriever() 