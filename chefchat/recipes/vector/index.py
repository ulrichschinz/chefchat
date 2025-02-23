import faiss
import numpy as np
import os
import json
from django.conf import settings
from chefchat.config import FAISS_INDEX_FILE, FAISS_MAPPING_FILE
from recipes.models import Recipe
from .embeddings import generate_embedding

def build_faiss_index(recipes):
    embeddings = []
    mapping = []
    for recipe in recipes:
        # Combine relevant fields into a single text string
        text = f"{recipe.title}\n{recipe.ingredients_raw}\n{recipe.instructions}"
        emb = generate_embedding(text)
        embeddings.append(emb)
        mapping.append(recipe.id)
    embeddings = np.vstack(embeddings)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index,mapping

def save_index_with_mapping(index, mapping):
    """
    Save the FAISS index and its associated mapping.
    """
    with open(FAISS_INDEX_FILE, "wb") as f:
        faiss.write_index(index, str(FAISS_INDEX_FILE))
    with open(FAISS_MAPPING_FILE, 'w') as f:
        json.dump(mapping, f)


def load_index_with_mapping():
    """
    Load the FAISS index and mapping from disk.
    """
    if FAISS_INDEX_FILE.exists() and FAISS_MAPPING_FILE.exists():
        index = faiss.read_index(str(FAISS_INDEX_FILE))
        with open(FAISS_MAPPING_FILE, 'r') as f:
            mapping = json.load(f)
        return index, mapping
    return None, None


def query_index_with_context(query_text: str, k: int = 5):
    """
    Query the FAISS index using the query text and return a list of matching recipe IDs and the distances.
    """
    query_embedding = generate_embedding(query_text).reshape(1, -1)
    index, mapping = load_index_with_mapping()
    if index is None or mapping is None:
        raise Exception("Index or mapping not found. Please rebuild the index first.")
    distances, indices = index.search(query_embedding, k)
    # Map FAISS indices to recipe IDs.
    recipe_ids = [mapping[i] for i in indices[0] if i < len(mapping)]
    return recipe_ids, distances