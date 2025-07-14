import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Mapbox token and input directory
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")
INPUT_DIR = Path(os.getenv("INPUT_DIR", "./data"))
PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", "./data/processed"))
REPROCESS_DIR = Path(os.getenv("REPROCESS_DIR", "./data/reprocessar"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
