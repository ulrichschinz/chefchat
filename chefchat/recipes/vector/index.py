import numpy as np
import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
from chefchat.config import QDRANT_COLLECTION_NAME
from .embeddings import generate_embedding
from recipes.models import QdrantMapping

client = QdrantClient(url="http://localhost:6333")
log = logging.getLogger(__name__)

def build_qdrant_index(user_id, items, text_fields, id_field):
    embeddings = []
    points = []
    for item in items:
        # Combine relevant fields into a single text string
        log.debug(f"Building index for item {item}")
        log.debug(f"textfields: {text_fields}")
        text = "\n".join([item[field] for field in text_fields])
        emb = generate_embedding(text)
        embeddings.append(emb)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=emb.tolist(),
            payload={
                'user_id': user_id,
                'title': item.get('title', ''),
                'type': item.get('type', 'unknown'),
                'additional_info': item.get('additional_info', ''),
                'original_id': f"{user_id}_{item[id_field]}"
            }
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

def query_index_with_context(user_id, query_text: str, k: int = 5):
    """
    Query the Qdrant index using the query text and return a list of matching items and the distances.
    """
    query_embedding = generate_embedding(query_text).tolist()
    search_filter = Filter(
        must=[
            FieldCondition(
                key="payload.user_id",
                match=MatchValue(value=user_id)
            )
        ]
    )
    search_result = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_embedding,
        limit=k,
        query_filter=search_filter
    )

    # Load mapping from database
    mapping = {mapping.point_id: mapping.payload
               for mapping in QdrantMapping.objects.all()}

    # Map Qdrant results to items
    results = []
    for result in search_result:
        item = mapping.get(result.id)
        if item:
            item['distance'] = result.score
            results.append(item)
    return results