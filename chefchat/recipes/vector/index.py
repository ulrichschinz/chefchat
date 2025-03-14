import logging
import uuid
import json
from django.contrib.auth import get_user_model
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
from chefchat.config import QDRANT_COLLECTION_NAME
from .embeddings import generate_embedding
from recipes.models import QdrantMapping
from recipes.services.index_builder import build_index_items

client = QdrantClient(url="http://localhost:6333")
log = logging.getLogger(__name__)

def convert_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: convert_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets(item) for item in obj]
    else:
        return obj

def build_qdrant_index(user, items, text_fields, id_field):
    embeddings = []
    points = []
    for item in items:
        # Combine relevant fields into a single text string
        text = "\n".join([item[field] for field in text_fields])
        emb = generate_embedding(text)
        embeddings.append(emb)
        payload = {
            'user_id': user.id,
            'title': item.get('title', ''),
            'type': item.get('type', 'unknown'),
            'additional_info': item.get('additional_info', ''),
            'original_id': f"{user.id}_{item.get(id_field, '')}"
        }
        # Ensure payload does not contain sets
        payload = convert_sets(payload)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=emb.tolist(),
            payload=payload
        ))
    # Create collection if it doesn't exist
    client.recreate_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE)
    )

    # Upload points to Qdrant
    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=points
    )

    # Save mapping to database
    for point in points:
        QdrantMapping.objects.update_or_create(
            point_id=point.id,
            defaults={'payload': point.payload}
        )

    return points

def query_index_with_context(user, query_text: str, k: int = 5):
    """
    Query the Qdrant index using the query text and return a list of matching items and the distances.
    """
    query_embedding = generate_embedding(query_text).tolist()

    # Create the filter for the user_id
    search_filter = Filter(
        must=[
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user.id)
            )
        ]
    )

    # Perform the search with the filter
    search_result = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_embedding,
        limit=k,
        query_filter=search_filter
    )

    # Load mapping from database
    mapping = {mapping.point_id: mapping.payload for mapping in QdrantMapping.objects.filter(payload__user_id=user.id)}

    # Map Qdrant results to items
    results = []
    for result in search_result:
        item = mapping.get(result.id)
        if item:
            item['distance'] = result.score
            results.append(item)
    return results

def rebuild_index():
    User = get_user_model()
    all_users = User.objects.all()
    for user in all_users:
        items = build_index_items(user)
        log.debug(f"Items: {len(items)}")
        build_qdrant_index(user, items, text_fields=['title', 'content'], id_field='id')
    log.debug("Index rebuilt")
