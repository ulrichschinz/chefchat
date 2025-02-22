from openai import OpenAI
import numpy as np
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embedding(text: str) -> np.ndarray:
    """
    Generate an embedding for the given text.
    """
    response = client.embeddings.create(model="text-embedding-ada-002", input=[text])
    embedding = response.data[0].embedding
    return np.array(embedding, dtype='float32')
