# main.py

import os
import sys
import hashlib
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

# LangChain and Ollama imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Local module imports
from src import config
from src import processing

# --- CLI Setup ---
console = Console()

def print_header():
    console.print(Panel.fit(
        "[bold green]SageScript Multi-Modal[/bold green]\nYour Unified Code & Image Assistant",
        border_style="green"
    ))

def build_unified_index(workspace_path: str, persist_dir: str):
    """
    Orchestrates the indexing of a workspace.
    - Identifies file types (image, code).
    - Routes to the appropriate processing function.
    - Creates a unified set of documents for embedding.
    """
    documents_to_embed = []
    
    console.print(f"[yellow]Scanning workspace: '{workspace_path}'...[/yellow]")
    
    all_files = []
    for root, _, files in os.walk(workspace_path):
        for file in files:
            all_files.append(os.path.join(root, file))

    if not all_files:
        console.print("[bold red]No files found in the workspace.[/bold red]")
        return None

    with console.status("[bold yellow]Processing files...[/bold yellow]") as status:
        for i, file_path in enumerate(all_files):
            file_name = os.path.basename(file_path)
            status.update(f"[yellow]Processing '{file_name}' ({i+1}/{len(all_files)})...[/yellow]")
            
            _, ext = os.path.splitext(file_path)
            
            content = None
            file_type = "other"

            # --- ORCHESTRATION LOGIC ---
            if ext.lower() in config.SUPPORTED_IMAGE_EXTENSIONS:
                content = processing.get_image_description(file_path)
                file_type = "image"
            elif ext.lower() in config.SUPPORTED_CODE_EXTENSIONS:
                content = processing.get_code_content(file_path)
                file_type = "code"

            if content:
                # We create a LangChain Document for each file/description
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": file_path,
                        "file_type": file_type
                    }
                )
                documents_to_embed.append(doc)

    if not documents_to_embed:
        console.print("[bold red]No processable content found to index.[/bold red]")
        return None

    console.print(f"[green]✅ Processed {len(documents_to_embed)} items. Now splitting and embedding...[/green]")

    # Split code documents, but keep image descriptions whole
    code_docs = [d for d in documents_to_embed if d.metadata["file_type"] == "code"]
    image_docs = [d for d in documents_to_embed if d.metadata["file_type"] == "image"]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    split_chunks = text_splitter.split_documents(code_docs)
    
    final_chunks = split_chunks + image_docs # Combine split code with whole image docs
    
    console.print(f"[green]✅ Created {len(final_chunks)} chunks. Generating embeddings...[/green]")

    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL, show_progress=True)
    vectorstore = Chroma.from_documents(
        documents=final_chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    console.print(f"\n[green]✅ Indexing complete! Database saved to '{persist_dir}'.[/green]\n")
    return vectorstore


def main():
    print_header()
    
    workspace_path = config.WORKSPACE_PATH
    if not os.path.isdir(workspace_path):
        console.print(f"[bold red]Workspace directory not found at '{workspace_path}'. Please create it.[/bold red]")
        sys.exit(1)

    # Use a hash of the path to create a unique DB directory
    db_id = hashlib.md5(os.path.abspath(workspace_path).encode()).hexdigest()
    persist_dir = os.path.join(config.CHROMA_PATH, db_id)

    vectorstore = None
    if os.path.isdir(persist_dir):
        if Prompt.ask(f"[yellow]Found existing index for '{workspace_path}'. Do you want to load it or re-index?[/yellow]", choices=["load", "re-index"], default="load") == "load":
            console.print(f"[green]Loading existing database from '{persist_dir}'...[/green]\n")
            embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
            vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        else:
            vectorstore = build_unified_index(workspace_path, persist_dir)
    else:
        console.print(f"[yellow]No index found for '{workspace_path}'. Indexing now...[/yellow]")
        vectorstore = build_unified_index(workspace_path, persist_dir)
    
    if not vectorstore:
        console.print("[bold red]Failed to initialize vector store. Exiting.[/bold red]")
        sys.exit(1)

    # --- Main Interaction Loop ---
    while True:
        prompt = Prompt.ask("\n[bold cyan]What are you looking for? (e.g., 'a function to parse json' or 'a picture of a cat on a red sofa')[/bold cyan]")
        if prompt.lower() == 'exit':
            break

        console.print("[yellow]🔍 Searching the unified index...[/yellow]")
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        retrieved_docs = retriever.invoke(prompt)
        
        console.print("\n--- [bold green]Top Search Results[/bold green] ---")
        if not retrieved_docs:
            console.print("[yellow]No relevant results found.[/yellow]")
            continue
            
        for doc in retrieved_docs:
            file_type = doc.metadata.get('file_type', 'unknown')
            source_path = doc.metadata.get('source', 'unknown')
            
            if file_type == 'image':
                panel_title = "🖼️ Found Image"
                panel_color = "magenta"
                content_display = f"[bold]Path:[/bold] [cyan]{source_path}[/cyan]\n\n[bold]Description:[/bold]\n[italic]{doc.page_content}[/italic]"
            else: # Code or text
                panel_title = "📝 Found Code/Text"
                panel_color = "blue"
                content_display = Syntax(doc.page_content, "python", theme="monokai", line_numbers=True, word_wrap=True)
                console.print(Panel(f"[bold]Source File:[/bold] [cyan]{source_path}[/cyan]", border_style=panel_color, expand=False))

            console.print(Panel(content_display, title=panel_title, border_style=panel_color, expand=False))
            console.print()

if __name__ == "__main__":
    main()