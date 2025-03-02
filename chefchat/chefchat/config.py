import os
from pathlib import Path

# Base directory for file paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Read the OpenAI API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")

# Qdrant collection
QDRANT_COLLECTION_NAME = "chefchat"
