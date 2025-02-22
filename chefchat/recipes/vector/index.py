import faiss
import numpy as np
import os
from django.conf import settings
from .embeddings import generate_embedding

def build_faiss_index(recipes):
    embeddings = []
    for recipe in recipes:
        # Combine relevant fields into a single text string
        text = f"{recipe.title}\n{recipe.ingredients_raw}\n{recipe.instructions}"
        emb = generate_embedding(text)
        embeddings.append(emb)
    embeddings = np.vstack(embeddings)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def save_index(index, filename: str):
    filepath = os.path.join(settings.BASE_DIR, filename)
    faiss.write_index(index, filepath)

def load_index(filename: str):
    filepath = os.path.join(settings.BASE_DIR, filename)
    if os.path.exists(filepath):
        return faiss.read_index(filepath)
    return None

def query_index(query_text: str, k: int = 5):
    query_embedding = generate_embedding(query_text).reshape(1, -1)
    index = load_index("faiss_index.index")
    if index is None:
        raise Exception("Index not found. Rebuild it first.")
    distances, indices = index.search(query_embedding, k)
    return distances, indices
