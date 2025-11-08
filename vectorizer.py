import json
import os
import boto3
from typing import List, Dict, Any, Tuple
import math
from datetime import datetime
from collections import defaultdict, Counter

# Inicializar clientes de AWS
s3_client = boto3.client("s3") # Para leer los datos crudos
s3vectors_client = boto3.client("s3vectors", region_name="us-east-1")
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")


# Configuración
RAW_DATA_BUCKET = os.getenv("S3_RAW_DATA_BUCKET", "lol-wrapped-data-lake")
VECTOR_INDEX_BUCKET = os.getenv("S3_VECTOR_INDEX_BUCKET", "lol-wrapped")
VECTOR_INDEX_NAME = os.getenv("S3_VECTOR_INDEX_NAME", "lol-wrapped-index")
BEDROCK_MODEL_ID = "amazon.titan-embed-text-v1"

def _get_player_puuid(player_identifier: str) -> str | None:
    """Obtiene el PUUID del jugador desde el archivo account-info.json."""
    try:
        key = f"riot_api_responses/{player_identifier}/account-info.json"
        obj = s3_client.get_object(Bucket=RAW_DATA_BUCKET, Key=key)
        data = json.loads(obj["Body"].read().decode("utf-8"))
        return data.get("puuid")
    except Exception as e:
        print(f"No se pudo obtener el PUUID para {player_identifier}: {e}")
        return None

def get_structured_player_data(player_identifier: str) -> List[Dict[str, Any]]:
    """
    Carga todos los datos JSON de un jugador desde S3 y los devuelve como datos estructurados.
    """
    prefix = f"riot_api_responses/{player_identifier}/"
    player_puuid = _get_player_puuid(player_identifier)
    if not player_puuid:
        return []

    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=RAW_DATA_BUCKET, Prefix=prefix)

    structured_data = []

    for page in pages:
        for content in page.get("Contents", []):
            key = content.get("Key")
            if not (key and key.endswith(".json")):
                continue

            obj = s3_client.get_object(Bucket=RAW_DATA_BUCKET, Key=key)
            try:
                data = json.loads(obj["Body"].read().decode("utf-8"))

                if "/matches/" in key:
                    info = data.get("info", {})
                    participant_data = next((p for p in info.get("participants", []) if p.get("puuid") == player_puuid), None)
                    if participant_data:
                        structured_data.append({
                            "type": "match_summary",
                            "gameId": info.get('gameId', 'N/A'),
                            "platformId": info.get('platformId', 'N/A'),
                            "gameStartTimestamp": info.get("gameStartTimestamp", 0),
                            "gameDuration": info.get("gameDuration", 0),
                            "championName": participant_data.get('championName', 'N/A'),
                            "win": participant_data.get('win', False),
                            "kills": participant_data.get('kills', 0),
                            "deaths": participant_data.get('deaths', 0),
                            "assists": participant_data.get('assists', 0),
                            "totalDamageDealtToChampions": participant_data.get('totalDamageDealtToChampions', 0),
                            "goldEarned": participant_data.get('goldEarned', 0),
                            "teamPosition": participant_data.get('teamPosition', 'N/A'),
                            "riotIdGameName": participant_data.get('riotIdGameName', 'N/A')
                        })
                else:
                    structured_data.append({
                        "type": "other_data", "source_file": key, "content": data
                    })
            except json.JSONDecodeError:
                print(f"Advertencia: No se pudo decodificar JSON del archivo: {key}")
    return structured_data

def create_all_level_chunks(player_identifier: str, structured_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Crea chunks de Nivel 1 (partida), Nivel 2 (campeón) y Nivel 3 (global)
    a partir de los datos estructurados.
    """
    all_chunks = []
    
    champion_stats = defaultdict(lambda: {'matches': 0, 'wins': 0, 'kills': 0, 'deaths': 0, 'assists': 0})
    global_stats = {'total_matches': 0, 'total_wins': 0, 'match_hours': [], 'roles': Counter()}
    
    match_data_list = [d for d in structured_data if d.get("type") == "match_summary"]

    for match_data in match_data_list:
        full_match_id = f"{match_data['platformId']}_{match_data['gameId']}"
        game_datetime_str = "Fecha desconocida"
        if match_data['gameStartTimestamp'] > 0:
            game_datetime = datetime.fromtimestamp(match_data['gameStartTimestamp'] / 1000)
            game_datetime_str = game_datetime.strftime("%d/%m/%Y a las %H:%M")
            global_stats['match_hours'].append(game_datetime.hour)

        summary = (
            f"Resumen de la partida con ID de partido {full_match_id}, jugada el {game_datetime_str}: "
            f"Jugador {match_data['riotIdGameName']} jugó como {match_data['championName']}. "
            f"Resultado: {'Victoria' if match_data['win'] else 'Derrota'}. "
            f"Duración: {round(match_data['gameDuration'] / 60)} minutos. "
            f"KDA: {match_data['kills']}/{match_data['deaths']}/{match_data['assists']}. "
        )
        all_chunks.append({"key": f"{player_identifier}-match-{full_match_id}", "content_text": summary})

        champ = match_data['championName']
        champion_stats[champ]['matches'] += 1
        champion_stats[champ]['kills'] += match_data['kills']
        champion_stats[champ]['deaths'] += match_data['deaths']
        champion_stats[champ]['assists'] += match_data['assists']
        if match_data['win']:
            champion_stats[champ]['wins'] += 1
            global_stats['total_wins'] += 1
            
        global_stats['total_matches'] += 1
        if match_data['teamPosition']:
            global_stats['roles'][match_data['teamPosition']] += 1

    for champ, stats in champion_stats.items():
        win_rate = (stats['wins'] / stats['matches'] * 100) if stats['matches'] > 0 else 0
        avg_k = stats['kills'] / stats['matches'] if stats['matches'] > 0 else 0
        avg_d = stats['deaths'] / stats['matches'] if stats['matches'] > 0 else 0
        avg_a = stats['assists'] / stats['matches'] if stats['matches'] > 0 else 0
        
        summary = (
            f"Resumen del campeón {champ}: Jugaste un total de {stats['matches']} partidas. "
            f"Tu porcentaje de victorias es del {win_rate:.1f}%. "
            f"Tu KDA promedio es {avg_k:.1f}/{avg_d:.1f}/{avg_a:.1f}."
        )
        all_chunks.append({"key": f"{player_identifier}-champion-{champ.replace(' ', '')}", "content_text": summary})
        
    if global_stats['total_matches'] > 0:
        overall_win_rate = (global_stats['total_wins'] / global_stats['total_matches'] * 100)
        most_played_champs = sorted(champion_stats.items(), key=lambda item: item[1]['matches'], reverse=True)[:3]
        most_played_champs_str = ", ".join([f"{champ} ({stats['matches']} partidas)" for champ, stats in most_played_champs])
        most_common_role = global_stats['roles'].most_common(1)[0][0] if global_stats['roles'] else "N/A"
        most_active_hour_str = "No hay datos de horario"
        if global_stats['match_hours']:
            hour_counts = Counter(global_stats['match_hours'])
            most_active_hour = hour_counts.most_common(1)[0][0]
            most_active_hour_str = f"entre las {most_active_hour}:00 y las {most_active_hour+1}:00"

        summary = (
            f"Resumen global para {player_identifier}: Jugaste un total de {global_stats['total_matches']} partidas. "
            f"Tu porcentaje de victorias general es del {overall_win_rate:.1f}%. "
            f"Tus campeones más jugados son: {most_played_champs_str}. "
            f"El rol más frecuente es {most_common_role}. "
            f"Sueles jugar más a menudo {most_active_hour_str}."
        )
        all_chunks.append({"key": f"{player_identifier}-global-summary", "content_text": summary})

    for other_data in structured_data:
        if other_data.get("type") == "other_data":
            full_text = json.dumps(other_data['content'], ensure_ascii=False)
            chunk_size = 4000
            if len(full_text) <= chunk_size:
                all_chunks.append({"key": f"{player_identifier}-other-{os.path.basename(other_data['source_file'])}", "content_text": full_text})
            else:
                for i, j in enumerate(range(0, len(full_text), chunk_size)):
                    chunk_text = full_text[j:j + chunk_size]
                    all_chunks.append({"key": f"{player_identifier}-other-{os.path.basename(other_data['source_file'])}-part{i}", "content_text": chunk_text})
    return all_chunks

def batch_insert_vectors(player_identifier: str, chunks: List[Dict[str, Any]]):
    """Genera embeddings e inserta los datos en el índice de S3 Vectors en lotes."""
    print(f"Iniciando inserción de {len(chunks)} vectores para {player_identifier}...")
    
    vectors_to_put = []
    for chunk in chunks:
        text_to_embed = chunk["content_text"]
        
        body = json.dumps({"inputText": text_to_embed})
        response = bedrock_runtime.invoke_model(
            body=body, modelId=BEDROCK_MODEL_ID, accept="application/json", contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        embedding = response_body.get("embedding")

        if not embedding:
            print(f"Advertencia: No se pudo generar embedding para el chunk con clave {chunk['key']}")
            continue

        vectors_to_put.append({
            "key": chunk['key'],
            "data": {"float32": embedding},
            "metadata": {
                "player-identifier": player_identifier,
                "source_text": text_to_embed,
            }
        })

    batch_size = 20
    total_vectors = len(vectors_to_put)
    total_batches = math.ceil(total_vectors / batch_size)

    for i in range(0, total_vectors, batch_size):
        batch = vectors_to_put[i:i + batch_size]
        try:
            s3vectors_client.put_vectors(
                vectorBucketName=VECTOR_INDEX_BUCKET, indexName=VECTOR_INDEX_NAME, vectors=batch
            )
            current_batch_num = (i // batch_size) + 1
            vectors_processed = i + len(batch)
            print(f"Lote {current_batch_num}/{total_batches} insertado (vectores procesados: {vectors_processed}/{total_vectors}) para {player_identifier}")
        except Exception as e:
            print(f"Error al insertar lote de vectores: {e}")

    print(f"Inserción de vectores completada para {player_identifier}.")

def handler(event, context):
    """
    Lambda handler para el job de vectorización.
    Extrae, Agrega, Transforma y Carga (ETL) los datos crudos a un índice de S3 Vectors.
    """
    player_identifier = event.get("player_identifier")
    if not player_identifier:
        raise ValueError("El evento debe contener 'player_identifier'")

    print(f"Iniciando job de vectorización para: {player_identifier}")

    structured_data = get_structured_player_data(player_identifier)
    if not structured_data:
        print(f"No se encontraron datos crudos para {player_identifier}. Finalizando job.")
        return {"statusCode": 200, "body": "No data to process."}
    
    match_count = sum(1 for d in structured_data if d.get("type") == "match_summary")
    print(f"Se extrajeron datos estructurados de {match_count} partidas.")

    all_level_chunks = create_all_level_chunks(player_identifier, structured_data)
    print(f"Se generaron {len(all_level_chunks)} chunks en total (partidas, campeones y resumen global).")

    batch_insert_vectors(player_identifier, all_level_chunks)
    
    return {
        "statusCode": 200,
        "body": json.dumps(f"Proceso de vectorización con S3 Vectors completado para {player_identifier}")
    }

if __name__ == "__main__":
    print("--- EJECUTANDO PRUEBA LOCAL DEL VECTORIZER ---")
    
    test_player_identifier = "Elxs-LAN" 
    
    mock_event = {"player_identifier": test_player_identifier}
    
    result = handler(mock_event, None)
    
    print("--- RESULTADO DE LA PRUEBA ---")
    print(result)
    print("--- PRUEBA LOCAL FINALIZADA ---")
