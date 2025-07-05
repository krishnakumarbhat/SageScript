# src/processing.py

import ollama
import os
from PIL import Image
from rich.console import Console
from . import config

console = Console()

def get_image_description(image_path: str) -> str | None:
    """Generates a text description for an image using the vision model."""
    try:
        with Image.open(image_path) as img:
            img.verify()

        prompt_text = "Describe this image in detail, focusing on objects, people, and actions. Be objective and concise."
        
        response = ollama.generate(
            model=config.VISION_LLM_MODEL,
            prompt=prompt_text,
            images=[image_path],
            stream=False
        )
        return response.get('response', '').strip()
    except Exception as e:
        console.print(f"[bold red]Error processing image {os.path.basename(image_path)}: {e}[/bold red]")
        return None

def get_code_content(file_path: str) -> str | None:
    """Reads the content of a code/text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        console.print(f"[bold red]Error reading file {os.path.basename(file_path)}: {e}[/bold red]")
        return None
    
    
import os
import hashlib
from typing import Optional, Tuple, List
from tqdm import tqdm
from rich.console import Console
from chromadb.api.models.Collection import Collection

from ..config.config import config
from ..utils.cli import console

def process_codebase(codebase_path: str, client) -> Optional[Collection]:
    """Process and index the codebase files"""
    if not os.path.isdir(codebase_path):
        console.print("[bold red]Error: Path not found or is not a directory.[/bold red]")
        return None

    # Create a unique collection name from the path to avoid collisions
    collection_name = "codebase_" + hashlib.md5(codebase_path.encode()).hexdigest()

    try:
        # Check if the collection already exists
        collection = client.get_collection(name=collection_name)
        console.print(f"[green]✅ Codebase '{os.path.basename(codebase_path)}' is already indexed.[/green]\n")
        return collection
    except ValueError:
        # If it doesn't exist, create it and index the files
        console.print(f"[yellow]'{os.path.basename(codebase_path)}' not found in database. Indexing now...[/yellow]")
        return index_codebase(client, collection_name, codebase_path)

def index_codebase(client, collection_name: str, codebase_path: str) -> Optional[Collection]:
    """Index the codebase and create a new collection"""
    collection = client.create_collection(name=collection_name)
    documents, ids = get_codebase_documents(codebase_path)
    
    if documents:
        # Add documents to the collection
        collection.add(documents=documents, ids=ids)
        console.print(f"\n[green]✅ Indexing complete! Added {len(documents)} files to the database.[/green]\n")
        return collection
    else:
        console.print("[bold red]No valid code files found to index.[/bold red]")
        return None

def get_codebase_documents(codebase_path: str) -> Tuple[List[str], List[str]]:
    """Get documents and their IDs from the codebase"""
    documents = []
    ids = []
    
    # Use tqdm for a progress bar
    file_list = [os.path.join(root, file)
                 for root, _, files in os.walk(codebase_path)
                 for file in files if os.path.splitext(file)[1] in config.CODE_EXTENSIONS]

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
    
    return documents, ids
