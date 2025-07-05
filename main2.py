import ollama
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
import hashlib

# LangChain components
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


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
    code_start = response_text.find("```")
    if code_start != -1:
        code_end = response_text.rfind("```")
        if code_end > code_start:
            content = response_text[code_start + 3:code_end].strip()
            if content.startswith(('python', 'javascript', 'typescript', 'go')):
                content = content[content.find('\n') + 1:]
            return content.strip()
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

def load_and_process_codebase(codebase_path, persist_dir):
    """Loads, splits, and embeds the codebase into a Chroma vector store."""
    console.print("[yellow]Loading documents from the codebase...[/yellow]")
    
    # Use DirectoryLoader to load all files, then we will filter them
    # Using a generic TextLoader for all recognized extensions
    loader = DirectoryLoader(codebase_path, glob="**/*", loader_cls=TextLoader, use_multithreading=True, silent_errors=True, show_progress=True)
    all_docs = loader.load()

    # Filter documents based on the allowed extensions
    documents = [doc for doc in all_docs if os.path.splitext(doc.metadata.get('source', ''))[1] in CODE_EXTENSIONS]

    if not documents:
        console.print("[bold red]No valid code files found to index.[/bold red]")
        return None

    console.print(f"[green]✅ Loaded {len(documents)} files. Now splitting into chunks...[/green]")

    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    console.print(f"[green]✅ Split into {len(chunks)} chunks. Now generating embeddings...[/green]")

    # Initialize Ollama embeddings
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    # Create and persist the Chroma vector store from the chunks
    # This will handle embedding and storage in one step.
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )

    console.print(f"\n[green]✅ Indexing complete! Database saved to '{persist_dir}'.[/green]\n")
    return vectorstore


def main():
    """Main function to run the SageScript CLI."""
    print_header()
    vectorstore = None

    # --- Get and Process Codebase Path ---
    if Confirm.ask("[yellow]Do you want to specify a codebase directory to use as context?[/yellow]"):
        while True:
            codebase_path = Prompt.ask("[cyan]Enter the full path to your codebase directory[/cyan]", default="/media/pope/projecteo/github_proj/SageScript/codedb")
            if os.path.isdir(codebase_path):
                break
            else:
                console.print("[bold red]Error: Path not found or is not a directory. Please try again.[/bold red]")

        # Create a unique directory name for persistence from the path hash
        db_id = hashlib.md5(codebase_path.encode()).hexdigest()
        persist_dir = os.path.join(CHROMA_PATH, db_id)

        # Check if the database is already indexed and persisted
        if os.path.isdir(persist_dir):
            console.print(f"[green]✅ Codebase '{os.path.basename(codebase_path)}' is already indexed.[/green]")
            console.print(f"[yellow]Loading existing database from '{persist_dir}'...[/yellow]\n")
            embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
            vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        else:
            # If it doesn't exist, create it by processing the codebase
            console.print(f"[yellow]'{os.path.basename(codebase_path)}' not found in database. Indexing now...[/yellow]")
            vectorstore = load_and_process_codebase(codebase_path, persist_dir)
            if not vectorstore:
                sys.exit(1) # Exit if indexing failed
    else:
        # If user doesn't specify a path, we can't do RAG
        console.print("[yellow]Skipping RAG. The model will not have any codebase context.[/yellow]\n")
        
    # --- Main Interaction Loop ---
    while True:
        prompt = Prompt.ask("\n[bold cyan]Enter your coding request (or type 'exit' to quit)[/bold cyan]")
        if prompt.lower() == 'exit':
            break

        context_str = ""
        # If we have a vectorstore (RAG is enabled), retrieve context
        if vectorstore:
            console.print("[yellow]🔍 Searching for relevant context in the codebase...[/yellow]")
            
            # Use the LangChain retriever to find relevant documents
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            retrieved_docs = retriever.invoke(prompt)
            
            # Format the retrieved documents into a context string
            # Include file path metadata for better context
            context_pieces = []
            for doc in retrieved_docs:
                relative_path = os.path.relpath(doc.metadata.get('source', ''), codebase_path)
                context_pieces.append(f"// File: {relative_path}\n\n{doc.page_content}")
            context_str = "\n---\n".join(context_pieces)

        # --- Generate Response with Ollama ---
        full_prompt = create_llm_prompt(prompt, context_str)
        console.print("[yellow]🧠 Generating code with stable-code:3b...[/yellow]")
        
        try:
            response = ollama.generate(model=LLM_MODEL, prompt=full_prompt, stream=False)
            generated_code = clean_llm_output(response['response'])
            
            # --- Display and Save Output ---
            console.print("\n--- [bold green]Generated Code[/bold green] ---")
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