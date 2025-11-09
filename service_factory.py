# service_factory.py
from typing import Optional
from config import AppConfig
from db_manager import ChromaDBManager
from llm_service import LLMService
from image_service import ImageService

class ServiceFactory:
    """
    Factory class for creating service instances.
    Implements the Factory Pattern to centralize service creation logic.
    """
    
    @staticmethod
    def create_db_manager(config: AppConfig) -> ChromaDBManager:
        """
        Create a ChromaDBManager instance.
        
        Args:
            config: Application configuration
            
        Returns:
            Configured ChromaDBManager instance
        """
        return ChromaDBManager(
            db_path=config.db_path,
            good_collection_name=config.good_collection_name,
            bad_collection_name=config.bad_collection_name,
            model_name=config.model_name
        )
    
    @staticmethod
    def create_llm_service(config: AppConfig) -> LLMService:
        """
        Create a LLMService instance.
        
        Args:
            config: Application configuration
            
        Returns:
            Configured LLMService instance
        """
        return LLMService(
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            ollama_base_url=config.ollama_base_url
        )
    
    @staticmethod
    def create_image_service(config: AppConfig) -> Optional[ImageService]:
        """
        Create an ImageService instance if API key is available.
        
        Args:
            config: Application configuration
            
        Returns:
            Configured ImageService instance or None if API key is missing
        """
        if config.jigsawstack_api_key:
            return ImageService(api_key=config.jigsawstack_api_key)
        return None