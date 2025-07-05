# SageScript
opensourse code writer
SageScript
Your Local Codebase Assistant powered by Ollama and LangChain

Overview
SageScript is a command-line interface (CLI) tool designed to assist developers by leveraging a locally running Ollama large language model (stable-code:3b) to generate code snippets based on queries about your own codebase. It uses LangChain and ChromaDB to index and embed your local code files, enabling retrieval-augmented generation (RAG) for context-aware code generation.

Features
Local LLM-powered code generation: Uses Ollama's stable-code:3b model running locally for fast, private code generation.

Codebase indexing: Automatically loads, splits, and embeds your codebase files for semantic search.

Retrieval-Augmented Generation (RAG): Retrieves relevant code snippets from your project to provide precise, context-aware code completions.

Interactive CLI: Friendly terminal interface powered by Rich for prompts, progress bars, and syntax-highlighted output.

Multi-language support: Supports indexing common programming languages and text files (.py, .js, .ts, .go, .rs, .java, .c, .cpp, .h, .cs, .html, .css, .md, .txt).

Save generated code: Optionally save the generated code snippets to files.

Getting Started
Prerequisites
Python 3.8+

Ollama installed and running locally with the stable-code:3b model.

Access to a terminal/command line.

Installation
Clone this repository:

bash
git clone https://github.com/yourusername/SageScript.git
cd SageScript
Create and activate a Python virtual environment (recommended):

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install the required Python packages:

bash
pip install -r requirements.txt
Note: The requirements.txt should include:

text
ollama
rich
tqdm
langchain
langchain-community
chromadb
Ensure Ollama is running locally:

bash
ollama run stable-code:3b
Usage
Run the main CLI script:

bash
python main.py
Workflow
Specify Codebase Directory

You will be prompted to specify the path to your local codebase directory. This directory will be scanned and indexed.

Indexing

If the codebase has not been indexed before, SageScript will load, split, and embed your code files, saving the vector database locally for future use.

Enter Coding Requests

After indexing, you can type coding queries or requests. SageScript will:

Retrieve relevant code snippets from your indexed codebase.

Generate code completions using the Ollama LLM.

Display syntax-highlighted code output.

Optionally save the generated code to a file.

Exit

Type exit to quit the CLI.

Configuration
You can configure the following constants in main.py:

Variable	Description	Default Value
EMBEDDING_MODEL	Ollama embedding model used for vectorization	"nomic-embed-text"
LLM_MODEL	Ollama LLM model for code generation	"stable-code:3b"
CHROMA_PATH	Path to store ChromaDB persistent vector store	"/media/pope/projecteo/github_proj/SageScript/chroma_db"
CODE_EXTENSIONS	Set of file extensions to index	{'.py', '.js', '.ts', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.cs', '.html', '.css', '.md', '.txt'}
Architecture
Document Loading: Uses LangChain's DirectoryLoader and TextLoader to load code files from the specified directory.

Text Splitting: Uses RecursiveCharacterTextSplitter to split large files into manageable chunks for embedding.

Embedding: Uses Ollama's embedding model (nomic-embed-text) via LangChain community's OllamaEmbeddings.

Vector Store: Stores embeddings in a persistent ChromaDB vector database.

Retrieval: Queries the vector store to retrieve top-k relevant code chunks based on user queries.

LLM Prompting: Constructs a prompt combining retrieved context and user query, then sends it to Ollama's stable-code:3b model.

Output: Cleans and displays the generated code with syntax highlighting and optional saving.

Example
bash
$ python main.py
text
SageScript
Your Local Codebase Assistant

Powered by Ollama, running stable-code:3b locally.

Do you want to specify a codebase directory to use as context? (y/n): y
Enter the full path to your codebase directory: /home/user/projects/myapp

'myapp' not found in database. Indexing now...
Loading documents from the codebase...
✅ Loaded 120 files. Now splitting into chunks...
✅ Split into 350 chunks. Now generating embeddings...
✅ Indexing complete! Database saved to '/media/pope/projecteo/github_proj/SageScript/chroma_db/abc123def456'.

Enter your coding request (or type 'exit' to quit): Write a Python function to parse JSON files

🔍 Searching for relevant context in the codebase...
🧠 Generating code with stable-code:3b...

--- Generated Code ---
import json

def parse_json_file(filepath):
with open(filepath, 'r') as f:
return json.load(f)

text
---

Do you want to save this code to a file? (y/n): y
Enter filename (e.g., 'new_feature.py'): parse_json.py
✅ Code saved to 'parse_json.py'
Troubleshooting
Ollama not found or not running: Make sure Ollama is installed and the stable-code:3b model is running locally.

No valid code files found: Verify your codebase path and ensure it contains files with supported extensions.

Permission errors: Ensure you have read access to the codebase directory and write access to the ChromaDB path.

Slow indexing: Large codebases may take time to index; progress bars are shown during indexing.

Contributing
Contributions are welcome! Feel free to open issues or submit pull requests for improvements, bug fixes, or new features.

License
Specify your license here (e.g., MIT License).

Acknowledgments
Ollama for the local LLM and embedding models.

LangChain for document loading, splitting, and vector store abstractions.

ChromaDB for the vector database.

Rich for beautiful CLI output.

If you want me to generate a requirements.txt or any additional docs, just ask!