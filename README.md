# SageScript 🧙‍♂️

A powerful local code assistant powered by Ollama that helps you understand and work with your codebase more effectively.

## 🌟 Features

- **Local Code Context**: Processes and understands your entire codebase to provide contextually relevant responses
- **Powered by Ollama**: Uses the stable-code:3b model for code generation and understanding
- **RAG Implementation**: Utilizes ChromaDB for efficient code indexing and retrieval
- **Rich CLI Interface**: Interactive command-line interface with beautiful formatting and progress indicators
- **Code Generation**: Generates code snippets based on your queries and codebase context
- **File Management**: Option to save generated code directly to files

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Ollama installed with stable-code:3b model
- ChromaDB

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SageScript.git
cd SageScript
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is running with the required model:
```bash
ollama pull stable-code:3b
```

## 💻 Usage

1. Run the application:
```bash
python main.py
```

2. Choose whether to specify a codebase directory for context
3. Enter your coding requests
4. Review generated code
5. Optionally save the generated code to a file

## 🔧 Configuration

Key configuration settings can be found at the top of `main.py`:

- `EMBEDDING_MODEL`: Model used for text embeddings
- `LLM_MODEL`: Model used for code generation
- `CHROMA_PATH`: Path for ChromaDB storage
- `CODE_EXTENSIONS`: Supported file extensions for indexing

## 📁 Project Structure

```
SageScript/
├── src/
│   ├── utils/         # Utility functions and CLI tools
│   ├── processing/    # Code processing and indexing
│   └── config/       # Configuration management
├── chroma_db/         # ChromaDB storage
├── main.py           # Main application entry point
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for the local LLM capabilities
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Rich](https://rich.readthedocs.io/) for beautiful CLI formatting
