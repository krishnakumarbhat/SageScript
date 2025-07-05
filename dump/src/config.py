# src/config.py

# --- Model Configuration ---
# Use the small, quantized model for the VLM
VISION_LLM_MODEL = "llava:7b-v1.6-mistral-q3_K_M" 
CODE_LLM_MODEL = "stable-code:3b"
EMBEDDING_MODEL = "nomic-embed-text"

# --- Path Configuration ---
CHROMA_PATH = "./chroma_db"
WORKSPACE_PATH = "./workspace" # The directory to be indexed

# --- File Type Configuration ---
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'}
SUPPORTED_CODE_EXTENSIONS = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.cs', '.html', '.css', '.md', '.txt'}



from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """Configuration class using the Singleton pattern"""
    _instance = None
    
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "stable-code:3b"
    CHROMA_PATH: str = str(Path(__file__).parent.parent.parent / "chroma_db")
    CODE_EXTENSIONS: set = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.cs', '.html', '.css', '.md', '.txt'}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

config = Config()
