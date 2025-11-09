# config.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class AppConfig(BaseModel):
    """
    Configuration class for SageScript application.
    Follows the Single Responsibility Principle by separating configuration concerns.
    """
    model_name: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 4000
    ollama_base_url: str = "http://localhost:11434"
    db_path: str = "./db"
    good_collection_name: str = "good_practices"
    bad_collection_name: str = "bad_practices"
    jigsawstack_api_key: Optional[str] = None
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """
        Create an AppConfig instance from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            AppConfig instance with values from the dictionary
        """
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})