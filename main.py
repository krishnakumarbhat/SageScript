# main.py
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text

# Import the service classes and utility functions
from cli.db_manager import ChromaDBManager, PRACTICES_COLLECTION, BAD_PRACTICES_COLLECTION
from cli.llm_service import LLMService
from cli.utils import display_header, save_code_to_file, display_code, display_review
from cli.image_service import ImageService

class SageScriptApp:
    """
    An interactive, menu-driven application for generating, reviewing, and indexing code.
    """

    def __init__(self):
        """Initializes all necessary services and components."""
        # --- Configuration ---
        self.CHROMA_PATH = "chroma_db"
        self.EMBEDDING_MODEL = "nomic-embed-text"
        self.LLM_MODEL = "stable-code:3b"
        # Get your free key from https://app.jigsawstack.com/dashboard
        self.JIGSAW_API_KEY = "sk_4ee413bb647169fe504ec9fe92cfde10f4500a0c07ab69a013e49a67f83a523bf1af7130b08cf53e0f037337ed358990d21f6d7ec36cd8d749e007597a3b31a0024RxlLpyTuFb98jXTqSp" # <-- PASTE YOUR KEY HERE

        # --- Services ---
        self.console = Console()
        self.db_manager = ChromaDBManager(
            path=self.CHROMA_PATH,
            embedding_model_name=self.EMBEDDING_MODEL
        )
        self.llm_service = LLMService(model_name=self.LLM_MODEL)
        self.image_service = ImageService(api_key=self.JIGSAW_API_KEY) # <-- NEW

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
    
    # def _run_generate_from_image(self):
    #     """Handles the 'Generate Code from Image' workflow using the JigsawStack pipeline."""
    #     self.console.rule("[bold magenta]GENERATE FROM IMAGE (via Text Extraction)[/bold magenta]")
    #     while True:
    #         image_path = Prompt.ask("[cyan]Enter the path to the image[/cyan]")
    #         if os.path.isfile(image_path):
    #             break
    #         self.console.print(f"[bold red]Error:[/bold red] File not found at '{image_path}'. Please try again.")
        
    #     # Step 1: Extract text from the image
    #     with self.console.status("[yellow]🔍 Extracting text from image via JigsawStack...[/yellow]"):
    #         extracted_text = self.image_service.extract_text_from_image(image_path)
        
    #     if not extracted_text:
    #         self.console.print("[bold red]Could not extract text from the image. Aborting.[/bold red]")
    #         return
            
    #     self.console.print("[green]✅ Text extracted successfully![/green]")
    #     self.console.print(Panel(extracted_text, title="Extracted Text", border_style="cyan"))

    #     # Step 2: Generate code from the extracted text
    #     prompt = Prompt.ask("\n[cyan]Enter a description for the code to generate (e.g., 'Implement this in Python')")

    #     with self.console.status("[yellow]🧠 Generating code using extracted text...[/yellow]"):
    #         generated_code = self.llm_service.generate_code_from_image_text(
    #             user_prompt=prompt,
    #             image_text=extracted_text
    #         )

    #     display_code(generated_code)
    #     save_code_to_file(generated_code)
    
    def _run_generate_from_image(self):
        """Handles the 'Generate Code from Image' workflow using the JigsawStack vOCR pipeline."""
        self.console.rule("[bold magenta]GENERATE FROM IMAGE (via Structured Extraction)[/bold magenta]")
        while True:
            image_path = Prompt.ask("[cyan]Enter the path to the image[/cyan]")
            if os.path.isfile(image_path):
                break
            self.console.print(f"[bold red]Error:[/bold red] File not found at '{image_path}'. Please try again.")

        # --- NEW: Ask the user what to extract ---
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
            return

        # Step 1: Extract structured data from the image
        with self.console.status("[yellow]🔍 Extracting structured data from image...[/yellow]"):
            structured_data = self.image_service.extract_structured_data_from_image(
                image_path=image_path,
                extraction_prompts=extraction_prompts
            )

        if not structured_data:
            self.console.print("[bold red]Could not extract data from the image. Aborting.[/bold red]")
            return

        self.console.print("\n[green]✅ Data extracted successfully![/green]")
        self.console.print(Panel(structured_data, title="Extracted Key-Value Data", border_style="cyan"))

        # Step 2: Generate code from the structured data
        prompt = Prompt.ask("\n[cyan]Enter a final prompt for the code generator (e.g., 'Create an HTML form with this')")

        with self.console.status("[yellow]🧠 Generating code using extracted data...[/yellow]"):
            generated_code = self.llm_service.generate_code_from_structured_data(
                user_prompt=prompt,
                structured_data=structured_data
            )

        display_code(generated_code)
        save_code_to_file(generated_code)

    def run_generate(self):
        """Handles the 'Generate Code' workflow, offering text or image input."""
        self.console.rule("[bold green]GENERATE CODE[/bold green]")

        # Ask user for generation type
        use_image = Confirm.ask("\n[bold]Do you want to generate code from an image?[/bold]", default=False)
        
        if use_image:
            self._run_generate_from_image()
            return

        # --- Existing text-based generation flow ---
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

    def run_review(self):
        """Handles the 'Review a Code File' workflow."""
        self.console.rule("[bold yellow]REVIEW CODE[/bold yellow]")
        while True:
            file_path = Prompt.ask("[cyan]Enter the path to the code file you want to review[/cyan]")
            if os.path.isfile(file_path):
                break
            self.console.print(f"[bold red]Error:[/bold red] File not found at '{file_path}'. Please try again.")

        try:
            code_to_review = Path(file_path).read_text(encoding='utf-8')
        except Exception as e:
            self.console.print(f"[bold red]Error reading file: {e}[/bold red]")
            return

        context_files = IntPrompt.ask("[cyan]How many 'bad practice' examples should I check against?[/cyan]", default=3)

        with self.console.status("[yellow]🔍 Searching for relevant bad practices...[/yellow]"):
            context = self.db_manager.query_collection(BAD_PRACTICES_COLLECTION, query=code_to_review, n_results=context_files)

        if not context:
            self.console.print("[yellow]⚠️ No similar bad practices found. Reviewing without specific context.[/yellow]")

        with self.console.status("[yellow]🧠 Analyzing code and generating review...[/yellow]"):
            review_text = self.llm_service.generate_review(code_to_review=code_to_review, context=context)

        display_review(code_to_review, review_text)


    def run_index(self):
        """Handles the 'Index a Directory' workflow."""
        self.console.rule("[bold blue]INDEX DIRECTORY[/bold blue]")
        while True:
            dir_path = Prompt.ask("[cyan]Enter the path to the directory to index[/cyan]")
            if os.path.isdir(dir_path):
                break
            self.console.print(f"[bold red]Error:[/bold red] Directory not found at '{dir_path}'. Please try again.")

        collection = ""
        while True:
            choice = Prompt.ask(
                "[cyan]Is this code a [bold green]good[/bold green] practice or a [bold yellow]bad[/bold yellow] practice?[/cyan] ([green]good[/green]/[yellow]bad[/yellow])"
            ).lower()

            if choice == 'good':
                collection = PRACTICES_COLLECTION
                break
            elif choice == 'bad':
                collection = BAD_PRACTICES_COLLECTION
                break
            else:
                self.console.print("[bold red]Invalid choice.[/bold red] Please enter 'good' or 'bad'.")
        # --- END OF MODIFIED BLOCK ---

        self.console.print(Panel(
            f"Indexing files from [cyan]'{dir_path}'[/cyan] into the [bold green]'{collection}'[/bold green] collection.",
            title="[blue]Database Indexing[/blue]", border_style="blue"
        ))
        self.db_manager.index_directory(collection_name=collection, source_path=dir_path)

    def run(self):
        """The main loop for the application."""
        while True:
            self.display_main_menu()
            choice = Prompt.ask("[bold]Enter your choice[/bold]", choices=["1", "2", "3", "4"], default="1")

            if choice == "1":
                self.run_generate()
            elif choice == "2":
                self.run_review()
            elif choice == "3":
                self.run_index()
            elif choice == "4":
                self.console.print("\n[bold magenta]Goodbye![/bold magenta]\n")
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