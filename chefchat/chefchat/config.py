import os
from pathlib import Path

# Base directory for file paths
BASE_DIR = Path(__file__).resolve().parent

# Read the OpenAI API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")

# Define the file paths for the FAISS index and mapping
FAISS_INDEX_FILE = BASE_DIR / "faiss_index.index"
FAISS_MAPPING_FILE = BASE_DIR / "faiss_mapping.json"