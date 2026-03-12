# 🦙 Llamaball

**High-performance document chat and RAG system powered by Ollama**

[![PyPI version](https://badge.fury.io/py/llamaball.svg)](https://badge.fury.io/py/llamaball)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A local-first toolkit for document ingestion, embedding generation, and conversational AI interactions. Built for privacy and performance.

## ✨ Key Features

- **🏠 100% Local**: No external API calls, complete privacy
- **🚀 High Performance**: Multi-threaded processing with intelligent caching
- **📚 Smart Parsing**: 80+ file types with advanced chunking
- **💬 Interactive Chat**: Context-aware conversations with your documents
- **🔧 Developer-Friendly**: Full Python API with async support

## 🚀 Quick Start

### Installation & Setup

```bash
# Install
pip install llamaball

# Install Ollama (required)
# Visit https://ollama.ai/ for installation

# Pull recommended models
ollama pull llama3.2:1b          # Fast chat model
ollama pull nomic-embed-text     # Required for embeddings
```

### Basic Usage

```bash
# Ingest documents
llamaball ingest .

# Start chatting
llamaball chat

# Get help
llamaball --help
```

## 📋 CLI Commands

### Document Processing
```bash
llamaball ingest ./docs --recursive --chunk-size 1000
llamaball list --search "python" --type py
llamaball stats
```

### Chat Features
```bash
llamaball chat --model llama3.2:3b --temperature 0.7
```

### In-Chat Commands
- `/models` - List available models
- `/model <name>` - Switch models
- `/temp <0.0-2.0>` - Adjust creativity
- `/help` - Show all commands

## 🐍 Python API

```python
from llamaball import core

# Ingest documents
core.ingest_files("./docs", recursive=True)

# Search
results = core.search_embeddings("machine learning", top_k=5)

# Chat
response = core.chat("Explain neural networks", enable_context=True)
```

## ⚙️ Configuration

### Environment Variables
- `CHAT_MODEL`: Default chat model (default: `llama3.2:1b`)
- `EMBEDDING_MODEL`: Embedding model (default: `nomic-embed-text`)
- `OLLAMA_ENDPOINT`: Ollama server (default: `http://localhost:11434`)

### Supported File Types
- **Text**: `.txt`, `.md`, `.rst`, `.tex`
- **Code**: `.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.yaml`
- **Documents**: `.pdf`, `.docx`, `.csv`, `.xlsx`
- **Notebooks**: `.ipynb`

## 🔧 Development

```bash
# Clone and install
git clone https://github.com/coolhand/llamaball.git
cd llamaball
pip install -e .[dev]

# Run tests
pytest

# Format code
black llamaball/ tests/
```

## 📁 Project Structure

```
llamaball/
├── llamaball/          # Main package
│   ├── cli.py          # CLI interface
│   ├── core.py         # Core functionality
│   └── utils.py        # Utilities
├── tests/              # Test suite
├── docs/               # Documentation
└── README.md           # This file
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

**Created by Luke Steuber** - [lukesteuber.com](https://lukesteuber.com)
- Contact: luke@lukesteuber.com
- GitHub: [lukeslp](https://github.com/lukeslp)
- Support: [Tip Jar](https://usefulai.lemonsqueezy.com/buy/bf6ce1bd-85f5-4a09-ba10-191a670f74af)

---

*For detailed documentation, advanced features, and comprehensive examples, see the [full documentation](docs/).*
