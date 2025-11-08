import json
import os
import boto3
from typing import List, Dict, Any

# Inicializar clientes de AWS
s3vectors_client = boto3.client("s3vectors", region_name="us-east-1")
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

# Configuración
VECTOR_INDEX_BUCKET = os.getenv("S3_VECTOR_INDEX_BUCKET", "lol-wrapped")
VECTOR_INDEX_NAME = os.getenv("S3_VECTOR_INDEX_NAME", "lol-wrapped-index")
BEDROCK_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"
BEDROCK_LLM_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0" # Actualizado a Claude 4.5

def get_embedding(text: str) -> List[float]:
    """Genera un embedding para un texto usando Bedrock Titan."""
    body = json.dumps({"inputText": text})
    response = bedrock_runtime.invoke_model(
        body=body, modelId=BEDROCK_EMBEDDING_MODEL_ID, accept="application/json", contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())
    return response_body.get("embedding")

def search_vectors_in_s3(player_identifier: str, query_embedding: List[float]) -> List[str]:
    """Busca en el índice de S3 Vectors y devuelve los textos fuente de los chunks relevantes."""
    print(f"Buscando en S3 Vectors para {player_identifier}...")
    try:
        response = s3vectors_client.query_vectors(
            vectorBucketName=VECTOR_INDEX_BUCKET,
            indexName=VECTOR_INDEX_NAME,
            queryVector={"float32": query_embedding},
            topK=5,  # Aumentamos significativamente el número de resultados
            filter={
                "metadata": {
                    "player-identifier": player_identifier
                }
            }
        )
        
        # Extraer el texto original del metadato
        relevant_chunks = [
            vector.get("metadata", {}).get("source_text", "")
            for vector in response.get("vectors", [])
        ]
        return [chunk for chunk in relevant_chunks if chunk]

    except Exception as e:
        print(f"Error al buscar en S3 Vectors: {e}")

def generate_response(query: str, context_chunks: List[str]) -> str:
    """Genera una respuesta usando el modelo de Bedrock con el contexto proporcionado."""
    context = "\n---\n".join(context_chunks)
    
    system_prompt = "Eres un experto analista de datos de League of Legends. Responde la pregunta del usuario basándote únicamente en el contexto proporcionado. Sé conciso, amigable y directo."
    
    messages = [
        {
            "role": "user",
            "content": [{"text": f"Contexto:\n{context}\n\nPregunta: {query}"}]
        }
    ]

    response = bedrock_runtime.converse(
        modelId=BEDROCK_LLM_MODEL_ID,
        messages=messages,
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0.1}
    )
    
    return response['output']['message']['content'][0]['text']

def handler(event, context):
    """
    Lambda handler para el agente RAG que responde preguntas sobre el Wrapped
    usando S3 Vectors para la búsqueda.
    """
    body = json.loads(event.get("body", "{}"))
    player_identifier = body.get("player_identifier")
    query = body.get("query")

    if not player_identifier or not query:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Los campos 'player_identifier' y 'query' son requeridos."})
        }

    print(f"Recibida pregunta para '{player_identifier}': '{query}'")

    try:
        # 1. Generar embedding para la pregunta del usuario
        query_embedding = get_embedding(query)
        
        # 2. Buscar en S3 Vectors para encontrar los fragmentos más relevantes
        relevant_chunks = search_vectors_in_s3(player_identifier, query_embedding)
        
        if not relevant_chunks:
            return {
                "statusCode": 404,
                "body": json.dumps({"answer": "No encontré información relevante en tus estadísticas para responder a esa pregunta."})
            }

        # 3. Generar la respuesta final con el contexto encontrado
        answer = generate_response(query, relevant_chunks)
        
        print(f"Respuesta generada: {answer}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({"answer": answer})
        }

    except Exception as e:
        print(f"Error fatal en el handler: {e}")
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Ocurrió un error interno al procesar la solicitud."})
        }


if __name__ == "__main__":
    # Evento de prueba para ejecución local
    print("--- EJECUTANDO PRUEBA LOCAL DEL AGENTE RAG ---")
    
    # Reemplaza con el identificador del jugador y una pregunta
    test_player_identifier = "Elxs-LAN"
    test_query = "¿Cuál fue mi mejor partida?"
    
    mock_event = {
        "body": json.dumps({
            "player_identifier": test_player_identifier,
            "query": test_query
        })
    }
    
    # Llamar al handler directamente
    result = handler(mock_event, None)
    
    print("--- RESULTADO DE LA PRUEBA ---")
    # Pretty print the JSON body
    if "body" in result:
        try:
            body_content = json.loads(result["body"])
            print(json.dumps(body_content, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(result["body"])
    else:
        print(result)
    print("--- PRUEBA LOCAL FINALIZADA ---")
