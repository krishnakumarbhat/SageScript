# cli/db_manager.py
import os
from rich.console import Console

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Constants ---
PRACTICES_COLLECTION = "practices"
BAD_PRACTICES_COLLECTION = "bad_practices"
CODE_EXTENSIONS = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.cs', '.html', '.css', '.md', '.txt'}

console = Console()

class ChromaDBManager:
    def __init__(self, path: str, embedding_model_name: str):
        self.path = path
        self.embedding_function = OllamaEmbeddings(model=embedding_model_name, show_progress=True)
        self.vector_store = Chroma(
            persist_directory=self.path,
            embedding_function=self.embedding_function
        )

    def index_directory(self, collection_name: str, source_path: str):
        """Loads, splits, and embeds documents from a directory into a specific collection."""
        console.print(f"[yellow]Loading documents from [cyan]'{source_path}'[/cyan]...[/yellow]")

        loader = DirectoryLoader(
            source_path, glob="**/*", loader_cls=TextLoader, use_multithreading=True,
            silent_errors=True, show_progress=True
        )
        all_docs = loader.load()
        documents = [doc for doc in all_docs if os.path.splitext(doc.metadata.get('source', ''))[1] in CODE_EXTENSIONS]

        if not documents:
            console.print("[bold red]No valid code files found to index.[/bold red]")
            return

        console.print(f"[green]✅ Loaded {len(documents)} files. Splitting into chunks...[/green]")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        console.print(f"[green]✅ Split into {len(chunks)} chunks. Generating embeddings and adding to '[bold]{collection_name}[/bold]'...[/green]")

        self.vector_store.add_documents(documents=chunks, collection_name=collection_name)
        console.print(f"\n[bold green]✅ Indexing complete![/bold green] Added {len(chunks)} document chunks to the database.")

    def query_collection(self, collection_name: str, query: str, n_results: int) -> str:
        """Queries a collection and returns a formatted context string."""
        try:
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": n_results},
                # Note: The `collection_name` argument is not a standard part of `as_retriever`.
                # Chroma's retriever will search all collections unless the store is initialized
                # with a specific collection name. A better approach for multi-collection is
                # to get the collection object first. However, for this setup, we rely on the
                # embedding search to span across data added with different collection names.
                # To be more precise, you would use:
                # self.vector_store.get(collection_name=collection_name).similarity_search(...)
                # but for LangChain's retriever interface, this works generally.
            )
            
            # To specifically query one collection, we need to manually use the Chroma client
            # The Langchain retriever wrapper isn't great for multiple collections. Let's do it right:
            docs = self.vector_store.similarity_search(query, k=n_results, collection_name=collection_name)

            if not docs:
                return ""

            context_pieces = []
            for doc in docs:
                file_path = doc.metadata.get('source', 'Unknown File')
                context_pieces.append(f"--- From: {file_path} ---\n{doc.page_content}")
            return "\n\n".join(context_pieces)

        except Exception as e:
            console.print(f"[yellow]⚠️ Could not query collection '{collection_name}'. It might be empty or not exist. Error: {e}[/yellow]")
            return ""