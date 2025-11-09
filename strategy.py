# strategy.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import os
from pathlib import Path
import typer
from rich.prompt import Prompt, Confirm

from db_manager import ChromaDBManager
from llm_service import LLMService
from image_service import ImageService
from command import TextBasedCodeGenerationCommand, CodeReviewCommand, DirectoryIndexingCommand, ImageBasedCodeGenerationCommand

class MenuStrategy(ABC):
    """
    Abstract base class for the Strategy Pattern.
    Defines a family of algorithms, encapsulates each one, and makes them interchangeable.
    """
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the strategy.
        
        Returns:
            bool: True if the application should continue, False if it should exit
        """
        pass

class GenerateCodeStrategy(MenuStrategy):
    """
    Strategy for generating code from text or image.
    """
    def __init__(self, 
                 llm_service: LLMService, 
                 image_service: Optional[ImageService] = None):
        """
        Initialize the strategy.
        
        Args:
            llm_service: Service for LLM interactions
            image_service: Optional service for image processing
        """
        self.llm_service = llm_service
        self.image_service = image_service
    
    def execute(self) -> bool:
        """
        Execute the code generation strategy.
        
        Returns:
            bool: True to continue the application
        """
        # Ask if the user wants to generate from an image
        from_image = Confirm.ask("Generate from image?") if self.image_service else False
        
        if from_image:
            self._run_generate_from_image()
        else:
            self._run_generate_from_text()
        
        return True
    
    def _run_generate_from_text(self) -> None:
        """
        Run the text-based code generation workflow.
        """
        user_input = Prompt.ask("What would you like to generate?")
        context = Prompt.ask("Any additional context? (optional)", default="")
        
        command = TextBasedCodeGenerationCommand(
            llm_service=self.llm_service,
            user_input=user_input,
            context=context if context else None
        )
        command.execute()
    
    def _run_generate_from_image(self) -> None:
        """
        Run the image-based code generation workflow.
        """
        if not self.image_service:
            print("Error: Image service is not available.")
            return
        
        # Get the image path
        image_path = Prompt.ask("Enter the path to the image file")
        if not os.path.exists(image_path):
            print(f"Error: File {image_path} does not exist.")
            return
        
        # Get extraction prompts
        extraction_prompts = [
            {"key": "language", "prompt": "What programming language is shown in the image?"},
            {"key": "description", "prompt": "Describe what the code in the image does."},
            {"key": "code_structure", "prompt": "What is the structure of the code (classes, functions, etc.)?"},
        ]
        
        # Extract structured data from the image
        structured_data = self.image_service.extract_structured_data_from_image(
            image_path, extraction_prompts
        )
        
        if not structured_data:
            print("Error: Failed to extract structured data from the image.")
            return
        
        # Create and execute the command
        command = ImageBasedCodeGenerationCommand(
            llm_service=self.llm_service,
            image_path=image_path,
            extraction_prompts=extraction_prompts,
            structured_data=structured_data
        )
        command.execute()

class ReviewCodeStrategy(MenuStrategy):
    """
    Strategy for reviewing code against bad practices.
    """
    def __init__(self, llm_service: LLMService, db_manager: ChromaDBManager):
        """
        Initialize the strategy.
        
        Args:
            llm_service: Service for LLM interactions
            db_manager: Database manager for retrieving examples
        """
        self.llm_service = llm_service
        self.db_manager = db_manager
    
    def execute(self) -> bool:
        """
        Execute the code review strategy.
        
        Returns:
            bool: True to continue the application
        """
        code_path = Prompt.ask("Enter the path to the code file to review")
        
        command = CodeReviewCommand(
            llm_service=self.llm_service,
            db_manager=self.db_manager,
            code_path=code_path
        )
        command.execute()
        
        return True

class IndexDirectoryStrategy(MenuStrategy):
    """
    Strategy for indexing directories into the database.
    """
    def __init__(self, db_manager: ChromaDBManager):
        """
        Initialize the strategy.
        
        Args:
            db_manager: Database manager for indexing
        """
        self.db_manager = db_manager
    
    def execute(self) -> bool:
        """
        Execute the directory indexing strategy.
        
        Returns:
            bool: True to continue the application
        """
        directory_path = Prompt.ask("Enter the path to the directory to index")
        collection_type = Prompt.ask(
            "Index as [g]ood or [b]ad practices?", 
            choices=["g", "b"]
        )
        
        collection_name = "good_practices" if collection_type == "g" else "bad_practices"
        
        command = DirectoryIndexingCommand(
            db_manager=self.db_manager,
            directory_path=directory_path,
            collection_name=collection_name
        )
        command.execute()
        
        return True

class ExitStrategy(MenuStrategy):
    """
    Strategy for exiting the application.
    """
    def execute(self) -> bool:
        """
        Execute the exit strategy.
        
        Returns:
            bool: False to exit the application
        """
        print("Exiting SageScript. Goodbye!")
        return False