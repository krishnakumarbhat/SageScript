# cli/utils.py
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()

def display_header():
    """Prints a fancy header for the project."""
    console.rule("[bold green]SageScript - Your Local Code Assistant[/bold green]")
    console.print()

def display_code(code: str):
    """Displays generated code with syntax highlighting."""
    console.print(Panel(
        Syntax(code, "python", theme="monokai", line_numbers=True),
        title="[bold green]Generated Code[/bold green]",
        border_style="green",
        expand=False
    ))

def display_review(original_code: str, review_text: str):
    """Displays the original code and its review side-by-side or one after another."""
    console.print(Panel(
        Syntax(original_code, "python", theme="monokai", line_numbers=True),
        title="[bold blue]Original Code[/bold blue]",
        border_style="blue",
        expand=False
    ))
    console.print(Panel(
        Markdown(review_text),
        title="[bold yellow]Code Review[/bold yellow]",
        border_style="yellow",
        expand=False
    ))

def save_code_to_file(code: str):
    """Asks the user if they want to save the code and saves it if confirmed."""
    if Confirm.ask("\n[yellow]Do you want to save this code to a file?[/yellow]"):
        filename = Prompt.ask("[cyan]Enter filename (e.g., 'new_feature.py')[/cyan]")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            console.print(f"[green]✅ Code saved to '{filename}'[/green]")
        except Exception as e:
            console.print(f"[bold red]Error saving file: {e}[/bold red]")