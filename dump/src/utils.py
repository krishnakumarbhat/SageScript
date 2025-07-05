from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

console = Console()

def print_header():
    """Prints a fancy header for the project."""
    console.print(Panel.fit(
        "[bold green]SageScript[/bold green]\nYour Local Codebase Assistant",
        border_style="green"
    ))
    console.print("\nPowered by Ollama, running [bold yellow]stable-code:3b[/bold yellow] locally.\n")

def display_code(generated_code: str):
    """Display generated code with syntax highlighting"""
    console.print("\n--- [bold green]Generated Code[/bold green] ---")
    syntax = Syntax(generated_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print("---")

def save_code_to_file(generated_code: str):
    """Save generated code to a file if user confirms"""
    if Confirm.ask("\n[yellow]Do you want to save this code to a file?[/yellow]"):
        filename = Prompt.ask("[cyan]Enter filename (e.g., 'new_feature.py')[/cyan]")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        console.print(f"[green]✅ Code saved to '{filename}'[/green]")
