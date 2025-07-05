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

        # --- Services ---
        self.console = Console()
        self.db_manager = ChromaDBManager(
            path=self.CHROMA_PATH,
            embedding_model_name=self.EMBEDDING_MODEL
        )
        self.llm_service = LLMService(model_name=self.LLM_MODEL)

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
            title="Main Menu",
            border_style="magenta",
            expand=False
        )
        self.console.print(menu)

    def run_generate(self):
        """Handles the 'Generate Code' workflow."""
        self.console.rule("[bold green]GENERATE CODE[/bold green]")
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