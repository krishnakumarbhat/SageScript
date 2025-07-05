# main.py
import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import os

from cli.db_manager import ChromaDBManager, PRACTICES_COLLECTION, BAD_PRACTICES_COLLECTION
from cli.llm_service import LLMService
from cli.utils import display_header, save_code_to_file, display_code, display_review

# --- Configuration ---
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "stable-code:3b"

# --- CLI App Setup ---
app = typer.Typer(
    name="SageScript",
    help="A local AI assistant to help generate and review code based on your custom knowledge bases.",
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()

# Initialize services
db_manager = ChromaDBManager(path=CHROMA_PATH, embedding_model_name=EMBEDDING_MODEL)
llm_service = LLMService(model_name=LLM_MODEL)


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="The description of the code you want to generate."),
    context_files: int = typer.Option(5, "--context", "-c", help="Number of relevant code examples to fetch from the 'practices' database.")
):
    """
    [bold green]Generates[/bold green] new code based on a prompt, using your 'practices' collection as context.
    """
    display_header()
    console.print(Panel(f"[bold]Query:[/bold] {prompt}", title="[cyan]Code Generation[/cyan]", border_style="cyan"))

    with console.status("[yellow]🔍 Searching for best practices...[/yellow]", spinner="earth"):
        context = db_manager.query_collection(PRACTICES_COLLECTION, prompt, n_results=context_files)

    if not context:
        console.print("[yellow]⚠️ No relevant practices found in the database. Generating without context.[/yellow]")

    with console.status("[yellow]🧠 Generating code with the LLM...[/yellow]", spinner="dots"):
        generated_code = llm_service.generate_code(user_prompt=prompt, context=context)

    display_code(generated_code)
    save_code_to_file(generated_code)


@app.command()
def review(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="The path to the code file you want to review."),
    context_files: int = typer.Option(3, "--context", "-c", help="Number of 'bad practice' examples to fetch for context.")
):
    """
    [bold yellow]Reviews[/bold yellow] an existing code file, checking it against your 'bad_practices' collection.
    """
    display_header()
    console.print(Panel(f"[bold]File to Review:[/bold] {file}", title="[cyan]Code Review[/cyan]", border_style="cyan"))

    try:
        code_to_review = file.read_text(encoding='utf-8')
    except Exception as e:
        console.print(f"[bold red]Error reading file: {e}[/bold red]")
        raise typer.Exit(1)

    with console.status("[yellow]🔍 Searching for relevant bad practices...[/yellow]", spinner="earth"):
        # The query to find bad practices is the code itself
        context = db_manager.query_collection(BAD_PRACTICES_COLLECTION, query=code_to_review, n_results=context_files)

    if not context:
        console.print("[yellow]⚠️ No similar bad practices found in the database. Reviewing without specific context.[/yellow]")

    with console.status("[yellow]🧠 Analyzing code and generating review...[/yellow]", spinner="dots"):
        review_text = llm_service.generate_review(code_to_review=code_to_review, context=context)

    display_review(code_to_review, review_text)


@app.command()
def index(
    directory: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True, help="The directory containing the code files to index."),
    collection: str = typer.Option(..., "--as", "-a", help=f"The collection to add the code to. Choose between '{PRACTICES_COLLECTION}' or '{BAD_PRACTICES_COLLECTION}'.")
):
    """
    [bold blue]Indexes[/bold blue] code from a directory into a specified collection ('practices' or 'bad_practices').
    """
    display_header()
    if collection not in [PRACTICES_COLLECTION, BAD_PRACTICES_COLLECTION]:
        console.print(f"[bold red]Error:[/bold red] Invalid collection '{collection}'.")
        console.print(f"Please choose either '[bold green]{PRACTICES_COLLECTION}[/bold green]' or '[bold yellow]{BAD_PRACTICES_COLLECTION}[/bold yellow]'.")
        raise typer.Exit(1)

    console.print(Panel(
        f"Indexing files from [cyan]'{directory}'[/cyan] into the [bold green]'{collection}'[/bold green] collection.",
        title="[blue]Database Indexing[/blue]", border_style="blue"
    ))
    db_manager.index_directory(collection_name=collection, source_path=str(directory))


if __name__ == "__main__":
    app()