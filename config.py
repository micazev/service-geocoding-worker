import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Mapbox token and input directory
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")
INPUT_DIR = Path(os.getenv("INPUT_DIR", "./data"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")