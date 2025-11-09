# main.py
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text

# Import the service classes and utility functions
from cli.db_manager import ChromaDBManager, PRACTICES_COLLECTION, BAD_PRACTICES_COLLECTION
from cli.llm_service import LLMService
from cli.utils import display_header, save_code_to_file, display_code, display_review
from cli.image_service import ImageService

# Configuration class following Single Responsibility Principle
class AppConfig:
    """Configuration settings for the SageScript application."""
    def __init__(self):
        self.chroma_path = "chroma_db"
        self.embedding_model = "nomic-embed-text"
        self.llm_model = "stable-code:3b"
        # Get your free key from https://app.jigsawstack.com/dashboard
        self.jigsaw_api_key = os.getenv("JIGSAWSTACK_API_KEY", "")

# Service Factory following Factory Pattern and Dependency Injection
class ServiceFactory:
    """Factory for creating service instances."""
    @staticmethod
    def create_db_manager(config: AppConfig) -> ChromaDBManager:
        return ChromaDBManager(
            path=config.chroma_path,
            embedding_model_name=config.embedding_model
        )
    
    @staticmethod
    def create_llm_service(config: AppConfig) -> LLMService:
        return LLMService(model_name=config.llm_model)
    
    @staticmethod
    def create_image_service(config: AppConfig) -> ImageService:
        try:
            return ImageService(api_key=config.jigsaw_api_key)
        except Exception:
            return None

class SageScriptApp:
    """
    An interactive, menu-driven application for generating, reviewing, and indexing code.
    Follows the Dependency Injection principle by accepting services through constructor.
    """

    def __init__(self, config: AppConfig = None):
        """Initializes all necessary services and components using dependency injection."""
        # Initialize configuration
        self.config = config or AppConfig()
        
        # Initialize console
        self.console = Console()
        
        # Initialize services using factory
        self.db_manager = ServiceFactory.create_db_manager(self.config)
        self.llm_service = ServiceFactory.create_llm_service(self.config)
        self.image_service = ServiceFactory.create_image_service(self.config)

    def display_main_menu(self):
        """Displays the main menu of the application."""
        display_header()
        menu = Panel(
            Text.from_markup(
                "[bold green]1.[/bold green] Generate Code\n"
                "[bold yellow]2.[/bold yellow] Review a Code File\n"
                "[bold blue]3.[/bold blue] Index a Directory\n\n"
                "[bold red]4.[/bold red] Exit"
            ),
            title="Main Menu", border_style="magenta", expand=False
        )
        self.console.print(menu)
    
    # Image processing workflow handler following Single Responsibility Principle
    class ImageWorkflowHandler:
        """Handles image processing workflows."""
        def __init__(self, console, image_service, llm_service):
            self.console = console
            self.image_service = image_service
            self.llm_service = llm_service
        
        def run_generate_from_image(self):
            """Handles the 'Generate Code from Image' workflow using the JigsawStack vOCR pipeline."""
            self.console.rule("[bold magenta]GENERATE FROM IMAGE (via Structured Extraction)[/bold magenta]")
            
            # Get image path
            image_path = self._get_valid_image_path()
            if not image_path:
                return
            
            # Get extraction prompts
            extraction_prompts = self._get_extraction_prompts()
            if not extraction_prompts:
                return
            
            # Extract data
            structured_data = self._extract_data_from_image(image_path, extraction_prompts)
            if not structured_data:
                return
            
            # Generate code
            self._generate_and_save_code(structured_data)
        
        def _get_valid_image_path(self):
            """Gets a valid image path from the user."""
            while True:
                image_path = Prompt.ask("[cyan]Enter the path to the image[/cyan]")
                if os.path.isfile(image_path):
                    return image_path
                self.console.print(f"[bold red]Error:[/bold red] File not found at '{image_path}'. Please try again.")
        
        def _get_extraction_prompts(self):
            """Gets extraction prompts from the user."""
            self.console.print("\n[bold]What specific fields do you want to extract from the image?[/bold]")
            self.console.print(" (e.g., 'username_field', 'password_field', 'submit_button_text')")
            self.console.print("Press Enter on an empty line when you are done.")
            
            extraction_prompts = []
            while True:
                item = Prompt.ask("[cyan]  -> Field to extract[/cyan]", default="")
                if not item:
                    break
                extraction_prompts.append(item.strip())
            
            if not extraction_prompts:
                self.console.print("[bold red]No fields were provided to extract. Aborting.[/bold red]")
                return None
            return extraction_prompts
        
        def _extract_data_from_image(self, image_path, extraction_prompts):
            """Extracts structured data from the image."""
            with self.console.status("[yellow]🔍 Extracting structured data from image...[/yellow]"):
                structured_data = self.image_service.extract_structured_data_from_image(
                    image_path=image_path,
                    extraction_prompts=extraction_prompts
                )

            if not structured_data:
                self.console.print("[bold red]Could not extract data from the image. Aborting.[/bold red]")
                return None

            self.console.print("\n[green]✅ Data extracted successfully![/green]")
            self.console.print(Panel(structured_data, title="Extracted Key-Value Data", border_style="cyan"))
            return structured_data
        
        def _generate_and_save_code(self, structured_data):
            """Generates and saves code from structured data."""
            prompt = Prompt.ask("\n[cyan]Enter a final prompt for the code generator (e.g., 'Create an HTML form with this')")

            with self.console.status("[yellow]🧠 Generating code using extracted data...[/yellow]"):
                generated_code = self.llm_service.generate_code_from_structured_data(
                    user_prompt=prompt,
                    structured_data=structured_data
                )

            display_code(generated_code)
            save_code_to_file(generated_code)
    
    def _run_generate_from_image(self):
        """Delegates to the ImageWorkflowHandler."""
        handler = self.ImageWorkflowHandler(self.console, self.image_service, self.llm_service)
        handler.run_generate_from_image()

    # Command Pattern implementation for workflows
    class Command:
        """Base command interface."""
        def execute(self):
            raise NotImplementedError("Subclasses must implement execute()")
    
    class TextBasedCodeGenerationCommand(Command):
        """Command for text-based code generation."""
        def __init__(self, console, db_manager, llm_service):
            self.console = console
            self.db_manager = db_manager
            self.llm_service = llm_service
        
        def execute(self):
            prompt = Prompt.ask("[cyan]Enter the description of the code you want to generate[/cyan]")
            context_files = IntPrompt.ask("[cyan]How many relevant examples should I use for context?[/cyan]", default=5)

            with self.console.status("[yellow]🔍 Searching for best practices...[/yellow]"):
                context = self.db_manager.query_collection(PRACTICES_COLLECTION, prompt, n_results=context_files)

            if not context:
                self.console.print("[yellow]⚠️ No relevant practices found. Generating without specific context.[/yellow]")

            with self.console.status("[yellow]🧠 Generating code...[/yellow]"):
                generated_code = self.llm_service.generate_code(user_prompt=prompt, context=context)

            display_code(generated_code)
            save_code_to_file(generated_code)
    
    class CodeReviewCommand(Command):
        """Command for code review."""
        def __init__(self, console, db_manager, llm_service):
            self.console = console
            self.db_manager = db_manager
            self.llm_service = llm_service
        
        def execute(self):
            self.console.rule("[bold yellow]REVIEW CODE[/bold yellow]")
            file_path = self._get_valid_file_path()
            if not file_path:
                return
            
            code_to_review = self._read_file_content(file_path)
            if not code_to_review:
                return
            
            context = self._get_bad_practices_context(code_to_review)
            review_text = self._generate_review(code_to_review, context)
            display_review(code_to_review, review_text)
        
        def _get_valid_file_path(self):
            """Gets a valid file path from the user."""
            while True:
                file_path = Prompt.ask("[cyan]Enter the path to the code file you want to review[/cyan]")
                if os.path.isfile(file_path):
                    return file_path
                self.console.print(f"[bold red]Error:[/bold red] File not found at '{file_path}'. Please try again.")
        
        def _read_file_content(self, file_path):
            """Reads the content of a file."""
            try:
                return Path(file_path).read_text(encoding='utf-8')
            except Exception as e:
                self.console.print(f"[bold red]Error reading file: {e}[/bold red]")
                return None
        
        def _get_bad_practices_context(self, code_to_review):
            """Gets bad practices context for the code review."""
            context_files = IntPrompt.ask("[cyan]How many 'bad practice' examples should I check against?[/cyan]", default=3)

            with self.console.status("[yellow]🔍 Searching for relevant bad practices...[/yellow]"):
                context = self.db_manager.query_collection(BAD_PRACTICES_COLLECTION, query=code_to_review, n_results=context_files)

            if not context:
                self.console.print("[yellow]⚠️ No similar bad practices found. Reviewing without specific context.[/yellow]")
            
            return context
        
        def _generate_review(self, code_to_review, context):
            """Generates a review for the code."""
            with self.console.status("[yellow]🧠 Analyzing code and generating review...[/yellow]"):
                return self.llm_service.generate_review(code_to_review=code_to_review, context=context)
    
    class DirectoryIndexingCommand(Command):
        """Command for directory indexing."""
        def __init__(self, console, db_manager):
            self.console = console
            self.db_manager = db_manager
        
        def execute(self):
            self.console.rule("[bold blue]INDEX DIRECTORY[/bold blue]")
            dir_path = self._get_valid_directory_path()
            if not dir_path:
                return
            
            collection = self._get_collection_type()
            if not collection:
                return
            
            self._index_directory(dir_path, collection)
        
        def _get_valid_directory_path(self):
            """Gets a valid directory path from the user."""
            while True:
                dir_path = Prompt.ask("[cyan]Enter the path to the directory to index[/cyan]")
                if os.path.isdir(dir_path):
                    return dir_path
                self.console.print(f"[bold red]Error:[/bold red] Directory not found at '{dir_path}'. Please try again.")
        
        def _get_collection_type(self):
            """Gets the collection type from the user."""
            while True:
                choice = Prompt.ask(
                    "[cyan]Is this code a [bold green]good[/bold green] practice or a [bold yellow]bad[/bold yellow] practice?[/cyan] ([green]good[/green]/[yellow]bad[/yellow])"
                ).lower()

                if choice == 'good':
                    return PRACTICES_COLLECTION
                elif choice == 'bad':
                    return BAD_PRACTICES_COLLECTION
                else:
                    self.console.print("[bold red]Invalid choice.[/bold red] Please enter 'good' or 'bad'.")
        
        def _index_directory(self, dir_path, collection):
            """Indexes a directory."""
            self.console.print(Panel(
                f"Indexing files from [cyan]'{dir_path}'[/cyan] into the [bold green]'{collection}'[/bold green] collection.",
                title="[blue]Database Indexing[/blue]", border_style="blue"
            ))
            self.db_manager.index_directory(collection_name=collection, source_path=dir_path)
    
    def run_generate(self):
        """Handles the 'Generate Code' workflow, offering text or image input."""
        self.console.rule("[bold green]GENERATE CODE[/bold green]")

        # Ask user for generation type
        use_image = False
        if self.image_service is not None:
            use_image = Confirm.ask("\n[bold]Do you want to generate code from an image?[/bold]", default=False)
        
        if use_image:
            self._run_generate_from_image()
            return

        # Use the command pattern for text-based generation
        command = self.TextBasedCodeGenerationCommand(self.console, self.db_manager, self.llm_service)
        command.execute()

    def run_review(self):
        """Handles the 'Review a Code File' workflow using Command pattern."""
        command = self.CodeReviewCommand(self.console, self.db_manager, self.llm_service)
        command.execute()

    def run_index(self):
        """Handles the 'Index a Directory' workflow using Command pattern."""
        command = self.DirectoryIndexingCommand(self.console, self.db_manager)
        command.execute()

    # Strategy Pattern for menu options
    class MenuStrategy:
        """Base strategy for menu options."""
        def execute(self, app):
            raise NotImplementedError("Subclasses must implement execute()")
    
    class GenerateCodeStrategy(MenuStrategy):
        """Strategy for generating code."""
        def execute(self, app):
            app.run_generate()
    
    class ReviewCodeStrategy(MenuStrategy):
        """Strategy for reviewing code."""
        def execute(self, app):
            app.run_review()
    
    class IndexDirectoryStrategy(MenuStrategy):
        """Strategy for indexing a directory."""
        def execute(self, app):
            app.run_index()
    
    class ExitStrategy(MenuStrategy):
        """Strategy for exiting the application."""
        def execute(self, app):
            app.console.print("\n[bold magenta]Goodbye![/bold magenta]\n")
            return True  # Signal to exit
    
    def run(self):
        """The main loop for the application using Strategy Pattern."""
        # Define strategies for menu options
        strategies = {
            "1": self.GenerateCodeStrategy(),
            "2": self.ReviewCodeStrategy(),
            "3": self.IndexDirectoryStrategy(),
            "4": self.ExitStrategy()
        }
        
        while True:
            self.display_main_menu()
            choice = Prompt.ask("[bold]Enter your choice[/bold]", choices=["1", "2", "3", "4"], default="1")
            
            # Execute the selected strategy
            should_exit = strategies[choice].execute(self)
            if should_exit:
                break
            
            # Pause for user to see the output before looping back to menu
            if Confirm.ask("\n[bold]Return to the main menu?[/bold]"):
                self.console.clear()
                continue
            else:
                self.console.print("\n[bold magenta]Goodbye![/bold magenta]\n")
                break


if __name__ == "__main__":
    from pathlib import Path
    app = SageScriptApp()
    app.run()