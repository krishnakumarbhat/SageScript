# command.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

from db_manager import ChromaDBManager
from llm_service import LLMService
from utils import display_code, display_review, save_code_to_file

class Command(ABC):
    """
    Abstract base class for the Command Pattern.
    Encapsulates a request as an object, allowing parameterization of clients with
    different requests and queue or log requests.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """
        Execute the command.
        """
        pass

class TextBasedCodeGenerationCommand(Command):
    """
    Command for generating code from text input.
    """
    def __init__(self, llm_service: LLMService, user_input: str, context: Optional[str] = None):
        """
        Initialize the command.
        
        Args:
            llm_service: Service for LLM interactions
            user_input: User's input text
            context: Optional context for code generation
        """
        self.llm_service = llm_service
        self.user_input = user_input
        self.context = context
    
    def execute(self) -> None:
        """
        Execute the code generation command.
        """
        generated_code = self.llm_service.generate_code(self.user_input, self.context)
        if generated_code:
            display_code(generated_code)
            save_code_to_file(generated_code)

class CodeReviewCommand(Command):
    """
    Command for reviewing code against bad practices.
    """
    def __init__(self, llm_service: LLMService, db_manager: ChromaDBManager, code_path: str):
        """
        Initialize the command.
        
        Args:
            llm_service: Service for LLM interactions
            db_manager: Database manager for retrieving examples
            code_path: Path to the code file to review
        """
        self.llm_service = llm_service
        self.db_manager = db_manager
        self.code_path = code_path
    
    def execute(self) -> None:
        """
        Execute the code review command.
        """
        if not os.path.exists(self.code_path):
            print(f"Error: File {self.code_path} does not exist.")
            return
        
        with open(self.code_path, "r") as f:
            code = f.read()
        
        # Get bad practice examples from the database
        bad_examples = self.db_manager.query_collection(
            "bad_practices", code, k=3
        )
        
        # Format the context with bad examples
        context = "\n\n".join([doc.page_content for doc in bad_examples]) if bad_examples else ""
        
        # Generate the review
        review = self.llm_service.generate_review(code, context)
        if review:
            display_review(code, review)

class DirectoryIndexingCommand(Command):
    """
    Command for indexing directories into the database.
    """
    def __init__(self, db_manager: ChromaDBManager, directory_path: str, collection_name: str):
        """
        Initialize the command.
        
        Args:
            db_manager: Database manager for indexing
            directory_path: Path to the directory to index
            collection_name: Name of the collection to index into
        """
        self.db_manager = db_manager
        self.directory_path = directory_path
        self.collection_name = collection_name
    
    def execute(self) -> None:
        """
        Execute the directory indexing command.
        """
        if not os.path.exists(self.directory_path) or not os.path.isdir(self.directory_path):
            print(f"Error: Directory {self.directory_path} does not exist.")
            return
        
        # Index the directory
        self.db_manager.index_directory(self.directory_path, self.collection_name)
        print(f"Successfully indexed {self.directory_path} into {self.collection_name} collection.")

class ImageBasedCodeGenerationCommand(Command):
    """
    Command for generating code from an image.
    """
    def __init__(self, 
                 llm_service: LLMService, 
                 image_path: str, 
                 extraction_prompts: List[Dict[str, str]],
                 structured_data: Dict[str, Any]):
        """
        Initialize the command.
        
        Args:
            llm_service: Service for LLM interactions
            image_path: Path to the image file
            extraction_prompts: Prompts for extracting data from the image
            structured_data: Structured data extracted from the image
        """
        self.llm_service = llm_service
        self.image_path = image_path
        self.extraction_prompts = extraction_prompts
        self.structured_data = structured_data
    
    def execute(self) -> None:
        """
        Execute the image-based code generation command.
        """
        if not self.structured_data:
            print("Error: Failed to extract structured data from the image.")
            return
        
        # Generate code from structured data
        generated_code = self.llm_service.generate_code_from_structured_data(
            self.structured_data
        )
        
        if generated_code:
            display_code(generated_code)
            save_code_to_file(generated_code)