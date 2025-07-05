import ollama
import chromadb
from typing import Optional
from rich.prompt import Prompt, Confirm

from src.config import config
from src.utils import console, print_header, display_code, save_code_to_file
from src.processing import process_codebase
from src.processing import clean_llm_output, create_llm_prompt

class SageScriptOrchestrator:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.CHROMA_PATH)
        self.collection = None
    
    def setup_codebase(self) -> None:
        """Set up and process the codebase if requested"""
        if Confirm.ask("[yellow]Do you want to specify a codebase directory to use as context?[/yellow]"):
            while True:
                codebase_path = Prompt.ask("[cyan]Enter the full path to your codebase directory[/cyan]")
                self.collection = process_codebase(codebase_path, self.client)
                if self.collection:
                    break
        else:
            console.print("[yellow]Skipping RAG. The model will not have any codebase context.[/yellow]\n")
    
    def process_query(self, prompt: str) -> Optional[str]:
        """Process a single query and return generated code"""
        context_str = ""
        if self.collection:
            console.print("[yellow]🔍 Searching for relevant context in the codebase...[/yellow]")
            results = self.collection.query(
                query_texts=[prompt],
                n_results=5
            )
            context_str = "\n---\n".join(results['documents'][0])

        full_prompt = create_llm_prompt(prompt, context_str)
        console.print("[yellow]🧠 Generating code with stable-code:3b...[/yellow]")
        
        try:
            response = ollama.generate(
                model=config.LLM_MODEL,
                prompt=full_prompt,
                stream=False
            )
            return clean_llm_output(response['response'])
        except Exception as e:
            console.print(f"[bold red]An error occurred while generating code: {e}[/bold red]")
            return None

    def run(self):
        """Main execution loop"""
        print_header()
        self.setup_codebase()

        while True:
            prompt = Prompt.ask("\n[bold cyan]Enter your coding request (or type 'exit' to quit)[/bold cyan]")
            if prompt.lower() == 'exit':
                break

            generated_code = self.process_query(prompt)
            if generated_code:
                display_code(generated_code)
                save_code_to_file(generated_code)
