"""
Configuration file for Airplane Search Engine
"""
import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
AIRPLANE_PHOTOS_DIR = os.path.join(DATA_DIR, 'airplane_photos')
EMBEDDINGS_DIR = os.path.join(DATA_DIR, 'embeddings')

# Static Files
STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

# Model Configuration
CLIP_MODEL_NAME = "openai/clip-vit-large-patch14"  # or "openai/clip-vit-base-patch32" for faster processing
EMBEDDING_DIM = 768  # For clip-vit-large-patch14 (512 for base model)

# Vector Database Configuration
FAISS_INDEX_PATH = os.path.join(EMBEDDINGS_DIR, 'airplane_index.faiss')
IMAGE_METADATA_PATH = os.path.join(EMBEDDINGS_DIR, 'image_metadata.json')

# Processing Configuration
BATCH_SIZE = 32  # Batch size for embedding generation
NUM_WORKERS = 4  # Number of workers for data loading
MAX_IMAGE_SIZE = (512, 512)  # Max size for image preprocessing

# Search Configuration
DEFAULT_TOP_K = 50  # Default number of search results to return
MAX_TOP_K = 100  # Maximum number of results allowed

# Flask Configuration
FLASK_DEBUG = False  # Disabled to prevent restart issues
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

# Allowed Image Extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

# Device Configuration (auto-detect GPU/CPU)
import torch

# Fix OpenMP conflict issue
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
