import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(override=True)

# gemini models
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_GENERATION_MODEL = "gemini-3.1-flash-lite"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"

# serpapi
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# data
DATA_DIR = Path(__file__).parent / "data"
ABHI_DATA_DIR = DATA_DIR / "abhi"
CARE_DATA_DIR = DATA_DIR / "care"
HDFC_DATA_DIR = DATA_DIR / "hdfc"
NIVA_DATA_DIR = DATA_DIR / "niva"
TEMP_DATA_DIR = DATA_DIR / "temp"

# storage
STORAGE_DIR = Path(__file__).parent / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
GENERATED_DIR = STORAGE_DIR / "generated"

# frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# create storage dirs
if not UPLOADS_DIR.exists():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
if not GENERATED_DIR.exists():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# create data dirs
if not ABHI_DATA_DIR.exists():
    ABHI_DATA_DIR.mkdir(parents=True, exist_ok=True)
if not CARE_DATA_DIR.exists():
    CARE_DATA_DIR.mkdir(parents=True, exist_ok=True)
if not HDFC_DATA_DIR.exists():
    HDFC_DATA_DIR.mkdir(parents=True, exist_ok=True)
if not NIVA_DATA_DIR.exists():
    NIVA_DATA_DIR.mkdir(parents=True, exist_ok=True)
if not TEMP_DATA_DIR.exists():
    TEMP_DATA_DIR.mkdir(parents=True, exist_ok=True)