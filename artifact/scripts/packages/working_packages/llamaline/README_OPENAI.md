# 🤖 Llamaline (OpenAI Version)

**A natural-language to shell/Python CLI assistant powered by OpenAI's API.**

This version of llamaline uses OpenAI's models (GPT-4, GPT-3.5-turbo, etc.) instead of local Ollama models, providing enhanced natural language understanding and code generation capabilities.

## ✨ Features

- 🧠 **Powered by OpenAI**: Uses GPT-4o-mini, GPT-4-turbo, or other OpenAI models
- 🗣️ **Natural Language Processing**: Type commands in plain English  
- 🛡️ **Safety First**: Confirmation prompts and unsafe operation blocking
- 🎨 **Rich Interface**: Colorized output with syntax highlighting
- ⚡ **Quick Commands**: Built-in cheat sheets for common tasks
- 🔄 **Model Flexibility**: Switch between OpenAI models on-the-fly
- 🎯 **Accessibility**: Full keyboard navigation, screen reader compatible

## 🚀 Quick Start

### Prerequisites

1. **OpenAI API Key**: You'll need an OpenAI API key
2. **Python 3.7+**: Make sure you have Python installed

### Installation

```bash
# Install dependencies
pip install -r requirements_openai.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Usage

#### Single Command Execution
```bash
python llamaline_openai.py "Show me disk usage"
python llamaline_openai.py "List all Python files in this directory"
python llamaline_openai.py "What's my current memory usage?"
```

#### Interactive Mode
```bash
python llamaline_openai.py
```

Then type natural language commands:
- `disk usage` → `df -h`
- `running processes` → `ps aux --sort -rss | head`
- `say hello` → `print('Hello, world!')`
- `git status` → `git status -sb`

#### Model Selection
```bash
# Use a specific model
python llamaline_openai.py -m gpt-4-turbo "analyze this log file"

# Or set environment variable
export OPENAI_MODEL="gpt-4-turbo"
python llamaline_openai.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Required: Your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Optional: Preferred model (default: gpt-4o-mini)
export OPENAI_MODEL="gpt-4o-mini"
```

### Available Models

The tool automatically detects available OpenAI models. Common options:
- `gpt-4o-mini` (default) - Fast and cost-effective
- `gpt-4-turbo` - Most capable for complex tasks
- `gpt-3.5-turbo` - Fast and affordable legacy option

## 🎯 Example Sessions

**System Administration:**
```
Enter your task (or 'quit' to exit): memory usage
⠋ Analyzing prompt with OpenAI...

💻 Bash Code Preview
vm_stat

Execute this code? [y/n] (y): y
⠙ Running bash code...

✅ Bash Output
Pages free:                   123456.
Pages active:                 234567.
...
```

**File Management:**
```
Enter your task: find all log files larger than 1MB
⠋ Analyzing prompt with OpenAI...

💻 Bash Code Preview  
find . -name "*.log" -size +1M -ls

Execute this code? [y/n] (y): y
⠙ Running bash code...

✅ Bash Output
-rw-r--r--    1 user  staff   2048000 Dec 19 10:30 ./app.log
...
```

## 📋 Built-in Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `cheats` | List all cheat sheet shortcuts |
| `model` | Show current model |
| `model <name>` | Switch to different OpenAI model |
| `history` | Show command history |
| `clear` | Clear the screen |
| `quit` | Exit the application |

## 💰 Cost Considerations

- **gpt-4o-mini**: ~$0.15 per million input tokens, very cost-effective
- **gpt-4-turbo**: ~$10 per million input tokens, most capable
- **gpt-3.5-turbo**: ~$0.50 per million input tokens, good balance

Most llamaline commands use 50-200 tokens, making costs very reasonable for typical usage.

## 🔒 Safety & Security

llamaline includes several safety features:
- **Command confirmation** before execution
- **Unsafe operation blocking** (prevents `sudo`, `rm -rf`, etc.)
- **Temporary file execution** for Python code
- **No persistent state** between commands
- **API key protection** (never logged or transmitted except to OpenAI)

## 🆚 Differences from Ollama Version

| Feature | Ollama Version | OpenAI Version |
|---------|---------------|----------------|
| **Models** | Local models (Llama, Gemma, etc.) | OpenAI models (GPT-4, etc.) |
| **Internet** | No internet required | Internet required |
| **Cost** | Free after setup | Pay-per-use |
| **Speed** | Fast (local inference) | Fast (cloud inference) |
| **Privacy** | Fully local | Data sent to OpenAI |
| **Setup** | Requires Ollama installation | Requires API key only |
| **Model Quality** | Good | Excellent |

## 🛠 Development

### File Structure
```
llamaline_openai.py     # Main OpenAI-powered CLI
requirements_openai.txt # OpenAI-specific dependencies  
README_OPENAI.md       # This file
```

### Key Differences from Original

1. **OpenAIChat Class**: Replaces `OllamaChat` with OpenAI API integration
2. **API Key Validation**: Checks for OPENAI_API_KEY on startup
3. **Model Listing**: Fetches available models from OpenAI API
4. **Error Handling**: OpenAI-specific error messages and handling

## 🌟 Contributing

Improvements welcome! The OpenAI version maintains the same interface as the original llamaline, making it easy to switch between local and cloud-based models.

## 📄 License

MIT License - same as original llamaline project.

---

**Made with ❤️ for developers who want the best of both worlds: local privacy with Ollama, or cloud power with OpenAI.** 