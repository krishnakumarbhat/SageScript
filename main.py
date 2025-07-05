import ollama
import chromadb
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from tqdm import tqdm
import hashlib
import langchain.document_loaders 
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# --- Configuration ---
# Define the models and ChromaDB path as constants for easy changes.
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "stable-code:3b"
CHROMA_PATH = "/media/pope/projecteo/github_proj/SageScript/chroma_db"
CODE_EXTENSIONS = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.cs', '.html', '.css', '.md', '.txt'}

# --- CLI Interface Setup using 'rich' library ---
console = Console()

def print_header():
    """Prints a fancy header for the project."""
    console.print(Panel.fit(
        "[bold green]SageScript[/bold green]\nYour Local Codebase Assistant",
        border_style="green"
    ))
    console.print("\nPowered by Ollama, running [bold yellow]stable-code:3b[/bold yellow] locally.\n")

def clean_llm_output(response_text):
    """Cleans the LLM output to extract only the code block."""
    # Find the start of a markdown code block
    code_start = response_text.find("```")
    if code_start != -1:
        # Find the end of the block
        code_end = response_text.rfind("```")
        if code_end > code_start:
            # Extract content between the fences
            content = response_text[code_start + 3:code_end].strip()
            # Remove the optional language identifier (e.g., 'python')
            if content.startswith(('python', 'javascript', 'typescript', 'go')):
                content = content[content.find('\n') + 1:]
            return content.strip()
    # If no markdown block is found, return the raw text stripped of whitespace
    return response_text.strip()

def create_llm_prompt(query, context):
    """Creates a structured prompt for the LLM."""
    return f"""
You are an expert programmer and a world-class coding assistant.
Your task is to answer the user's query based on the provided code context.
The context contains relevant code snippets from the user's local codebase.
Generate only the code required to fulfill the request. Do not add any conversational text, explanations, or markdown fences.

--- CONTEXT ---
{context}
--- END CONTEXT ---

USER QUERY: {query}

CODE:
"""

def main():
    """Main function to run the SageScript CLI."""
    print_header()

    # --- ChromaDB Setup ---
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # --- Get and Process Codebase Path ---
    if Confirm.ask("[yellow]Do you want to specify a codebase directory to use as context?[/yellow]"):
        while True:
            codebase_path = Prompt.ask("[cyan]Enter the full path to your codebase directory[/cyan]")
            if os.path.isdir(codebase_path):
                break
            else:
                codebase_path = '/media/pope/projecteo/github_proj/SageScript/codedb' # use this path by default
                console.print("[bold red]Error: Path not found or is not a directory. Please try again.[/bold red]")

        # Create a unique collection name from the path to avoid collisions
        collection_name = "codebase_" + hashlib.md5(codebase_path.encode()).hexdigest()

        try:
            # Check if the collection already exists
            collection = client.get_collection(name=collection_name)
            console.print(f"[green]✅ Codebase '{os.path.basename(codebase_path)}' is already indexed.[/green]\n")
        except ValueError:
            # If it doesn't exist, create it and index the files
            console.print(f"[yellow]'{os.path.basename(codebase_path)}' not found in database. Indexing now...[/yellow]")
            collection = client.create_collection(name=collection_name)

            documents = []
            ids = []
            
            # Use tqdm for a progress bar
            file_list = [os.path.join(root, file)
                         for root, _, files in os.walk(codebase_path)
                         for file in files if os.path.splitext(file)[1] in CODE_EXTENSIONS]

            with tqdm(total=len(file_list), desc="Indexing files", unit="file") as pbar:
                for file_path in file_list:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Use file path as ID and store it as a document
                        documents.append(f"// File: {os.path.relpath(file_path, codebase_path)}\n\n{content}")
                        ids.append(file_path)
                    except Exception as e:
                        console.print(f"\n[red]Skipping file {file_path}: {e}[/red]")
                    pbar.update(1)

            if documents:
                # Add documents to the collection. ChromaDB handles embedding automatically.
                collection.add(documents=documents, ids=ids)
                console.print(f"\n[green]✅ Indexing complete! Added {len(documents)} files to the database.[/green]\n")
            else:
                console.print("[bold red]No valid code files found to index.[/bold red]")
                sys.exit()
    else:
        # If user doesn't specify a path, we can't do RAG
        console.print("[yellow]Skipping RAG. The model will not have any codebase context.[/yellow]\n")
        collection = None


    # --- Main Interaction Loop ---
    while True:
        prompt = Prompt.ask("\n[bold cyan]Enter your coding request (or type 'exit' to quit)[/bold cyan]")
        if prompt.lower() == 'exit':
            break

        context_str = ""
        # If we have a collection (RAG is enabled), retrieve context
        if collection:
            console.print("[yellow]🔍 Searching for relevant context in the codebase...[/yellow]")
            results = collection.query(
                query_texts=[prompt],
                n_results=5 # Retrieve top 5 most relevant file snippets
            )
            # Combine the retrieved documents into a single context string
            context_str = "\n---\n".join(results['documents'][0])

        # --- Generate Response with Ollama ---
        full_prompt = create_llm_prompt(prompt, context_str)
        console.print("[yellow]🧠 Generating code with stable-code:3b...[/yellow]")
        
        try:
            response = ollama.generate(
                model=LLM_MODEL,
                prompt=full_prompt,
                stream=False # Set to False for a single response
            )

            generated_code = clean_llm_output(response['response'])
            
            # --- Display and Save Output ---
            console.print("\n--- [bold green]Generated Code[/bold green] ---")
            # Use Rich's Syntax to print the code with highlighting
            syntax = Syntax(generated_code, "python", theme="monokai", line_numbers=True)
            console.print(syntax)
            console.print("---")

            if Confirm.ask("\n[yellow]Do you want to save this code to a file?[/yellow]"):
                filename = Prompt.ask("[cyan]Enter filename (e.g., 'new_feature.py')[/cyan]")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(generated_code)
                console.print(f"[green]✅ Code saved to '{filename}'[/green]")

        except Exception as e:
            console.print(f"[bold red]An error occurred while generating code: {e}[/bold red]")


if __name__ == "__main__":
    main()