# Comprehensive Llamafile Setup for Vector Database RAG Applications

**Created by Luke Steuber** - [lukesteuber.com](https://lukesteuber.com) | [assisted.site](https://assisted.site)

MIT License - Copyright (c) 2025 Luke Steuber

This guide provides optimal llamafile configurations for building local RAG (Retrieval Augmented Generation) systems similar to your `doc_chat_ollama.py` implementation.

## Architecture Overview

For optimal RAG performance, we recommend running **two separate llamafiles**:
1. **Embedding Server** - Handles document vectorization and query embeddings
2. **Chat Server** - Handles text generation and conversation

## Recommended Model Configurations

### Tier 1: High-Performance Setup (16GB+ RAM)

#### Embedding Model: Nomic Embed v1.5
```bash
# Download the best overall embedding model for RAG
wget https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q4_K_M.gguf

# Create embedding server configuration
cat > embedding-server.args << 'EOF'
-m
nomic-embed-text-v1.5.Q4_K_M.gguf
--port
8081
--host
0.0.0.0
--embedding
--nobrowser
-c
8192
-b
8192
--rope-scaling
yarn
--rope-freq-scale
0.75
-ngl
99
...
EOF

# Create llamafile
cp /usr/local/bin/llamafile nomic-embed.llamafile
zipalign -j0 nomic-embed.llamafile nomic-embed-text-v1.5.Q4_K_M.gguf embedding-server.args
```

#### Chat Model: Llama 3 8B Instruct
```bash
# Download Llama 3 8B for high-quality chat
wget https://huggingface.co/Mozilla/Meta-Llama-3-8B-Instruct-llamafile/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.llamafile

# Create chat server configuration
cat > chat-server.args << 'EOF'
-m
Meta-Llama-3-8B-Instruct.Q4_K_M.gguf
--port
8080
--host
0.0.0.0
--chat-template
llama3
-c
8192
-ngl
35
-n
-1
--temp
0.2
--repeat-penalty
1.1
...
EOF

# Create llamafile
cp Meta-Llama-3-8B-Instruct.Q4_K_M.llamafile llama3-chat.llamafile
zipalign -j0 llama3-chat.llamafile Meta-Llama-3-8B-Instruct.Q4_K_M.gguf chat-server.args
```

### Tier 2: Balanced Setup (8-16GB RAM)

#### Embedding Model: MXBai Embed Large
```bash
# Download efficient embedding model
wget https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1-GGUF/resolve/main/mxbai-embed-large-v1.Q4_K_M.gguf

cat > mxbai-embed.args << 'EOF'
-m
mxbai-embed-large-v1.Q4_K_M.gguf
--port
8081
--host
0.0.0.0
--embedding
--nobrowser
-c
512
-b
512
-ngl
20
...
EOF
```

#### Chat Model: Mistral 7B Instruct v0.2
```bash
# Download Mistral 7B
wget https://huggingface.co/Mozilla/Mistral-7B-Instruct-v0.2-llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.llamafile

cat > mistral-chat.args << 'EOF'
-m
mistral-7b-instruct-v0.2.Q4_K_M.gguf
--port
8080
--host
0.0.0.0
-c
4096
-ngl
25
--temp
0.2
--repeat-penalty
1.1
-n
-1
...
EOF
```

### Tier 3: Lightweight Setup (4-8GB RAM)

#### Embedding Model: All-MiniLM
```bash
# Download lightweight embedding model
wget https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2-GGUF/resolve/main/all-MiniLM-L6-v2.Q4_K_M.gguf

cat > minilm-embed.args << 'EOF'
-m
all-MiniLM-L6-v2.Q4_K_M.gguf
--port
8081
--host
0.0.0.0
--embedding
--nobrowser
-c
512
-b
512
-ngl
10
...
EOF
```

#### Chat Model: TinyLlama 1.1B
```bash
# Download TinyLlama
wget https://huggingface.co/Mozilla/TinyLlama-1.1B-Chat-v1.0-llamafile/resolve/main/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile

cat > tinyllama-chat.args << 'EOF'
-m
TinyLlama-1.1B-Chat-v1.0.Q5_K_M.gguf
--port
8080
--host
0.0.0.0
-c
2048
-ngl
15
--temp
0.7
--repeat-penalty
1.1
-n
-1
...
EOF
```

## Startup Scripts

### Production RAG System Launcher
```bash
#!/bin/bash
# rag-system-start.sh

# Set hardware tier (1, 2, or 3)
TIER=${1:-2}

# Start embedding server in background
case $TIER in
    1)
        echo "Starting Tier 1: High-Performance RAG System"
        ./nomic-embed.llamafile &
        EMBED_PID=$!
        sleep 10
        ./llama3-chat.llamafile &
        CHAT_PID=$!
        ;;
    2)
        echo "Starting Tier 2: Balanced RAG System"
        ./mxbai-embed.llamafile &
        EMBED_PID=$!
        sleep 10
        ./mistral-chat.llamafile &
        CHAT_PID=$!
        ;;
    3)
        echo "Starting Tier 3: Lightweight RAG System"
        ./minilm-embed.llamafile &
        EMBED_PID=$!
        sleep 10
        ./tinyllama-chat.llamafile &
        CHAT_PID=$!
        ;;
esac

echo "Embedding server PID: $EMBED_PID"
echo "Chat server PID: $CHAT_PID"
echo "Embedding endpoint: http://localhost:8081"
echo "Chat endpoint: http://localhost:8080"

# Save PIDs for cleanup
echo $EMBED_PID > embed.pid
echo $CHAT_PID > chat.pid

# Wait for interrupt
trap 'kill $EMBED_PID $CHAT_PID' INT
wait
```

## Integration with Your doc_chat_ollama.py

### Modified Embedding Function
```python
import requests
import json
import numpy as np

def get_embedding_llamafile(text: str, model: str = "nomic-embed", base_url: str = "http://localhost:8081") -> np.ndarray:
    """Get embedding from llamafile embedding server"""
    
    # Add task prefix for nomic models
    if "nomic" in model.lower():
        text = f"search_document: {text}"
    
    payload = {
        "content": text,
        "n_predict": 0  # We only want embeddings
    }
    
    response = requests.post(f"{base_url}/embedding", json=payload)
    response.raise_for_status()
    
    embedding = response.json()["embedding"]
    return np.array(embedding, dtype=np.float32)

def get_chat_response_llamafile(messages: list, base_url: str = "http://localhost:8080") -> str:
    """Get chat response from llamafile chat server"""
    
    # Format messages for chat
    formatted_prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            formatted_prompt += f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{msg['content']}<|eot_id|>"
        elif msg["role"] == "user":
            formatted_prompt += f"<|start_header_id|>user<|end_header_id|>\n{msg['content']}<|eot_id|>"
        elif msg["role"] == "assistant":
            formatted_prompt += f"<|start_header_id|>assistant<|end_header_id|>\n{msg['content']}<|eot_id|>"
    
    formatted_prompt += "<|start_header_id|>assistant<|end_header_id|>\n"
    
    payload = {
        "prompt": formatted_prompt,
        "n_predict": 512,
        "temperature": 0.2,
        "stop": ["<|eot_id|>", "<|end_of_text|>"]
    }
    
    response = requests.post(f"{base_url}/completion", json=payload)
    response.raise_for_status()
    
    return response.json()["content"].strip()
```

### Updated Configuration in your script
```python
# Replace these variables in your doc_chat_ollama.py
DEFAULT_EMBEDDING_ENDPOINT = "http://localhost:8081"
DEFAULT_CHAT_ENDPOINT = "http://localhost:8080"
DEFAULT_MODEL_NAME = "nomic-embed"  # For embedding
DEFAULT_CHAT_MODEL = "llama3-chat"  # For chat
```

## Performance Optimization

### Embedding Server Optimization
```bash
# For batch processing documents
cat > batch-embed.args << 'EOF'
-m
nomic-embed-text-v1.5.Q4_K_M.gguf
--port
8081
--host
0.0.0.0
--embedding
--nobrowser
-c
8192
-b
64  # Larger batch size for document processing
--parallel
4   # Process multiple embeddings in parallel
-ngl
99
...
EOF
```

### Chat Server Optimization
```bash
# For interactive chat
cat > interactive-chat.args << 'EOF'
-m
Meta-Llama-3-8B-Instruct.Q4_K_M.gguf
--port
8080
--host
0.0.0.0
-c
8192
-ngl
35
--cache-type-k
f16  # Optimize KV cache
--cache-type-v
f16
--mlock     # Lock model in memory
--no-mmap   # Disable memory mapping for speed
...
EOF
```

## Docker Deployment (Optional)

```dockerfile
# Dockerfile.rag-system
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy llamafiles
COPY *.llamafile ./
RUN chmod +x *.llamafile

# Expose ports
EXPOSE 8080 8081

# Start script
COPY rag-system-start.sh ./
RUN chmod +x rag-system-start.sh

CMD ["./rag-system-start.sh", "2"]
```

## Testing Your Setup

```bash
# Test embedding endpoint
curl -X POST http://localhost:8081/embedding \
  -H "Content-Type: application/json" \
  -d '{"content": "search_document: What is artificial intelligence?"}'

# Test chat endpoint
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?", "n_predict": 100}'
```

## Monitoring and Maintenance

### Health Check Script
```bash
#!/bin/bash
# health-check.sh

echo "Checking RAG system health..."

# Check embedding server
if curl -sf http://localhost:8081/health > /dev/null; then
    echo "✓ Embedding server: Online"
else
    echo "✗ Embedding server: Offline"
fi

# Check chat server
if curl -sf http://localhost:8080/health > /dev/null; then
    echo "✓ Chat server: Online"
else
    echo "✗ Chat server: Offline"
fi
```

## Model Performance Characteristics

| Tier | Embedding Model | Chat Model | RAM Usage | Quality | Speed |
|------|----------------|------------|-----------|---------|-------|
| 1 | Nomic Embed v1.5 | Llama 3 8B | 16GB+ | Excellent | Fast |
| 2 | MXBai Large | Mistral 7B | 8-16GB | Very Good | Medium |
| 3 | All-MiniLM | TinyLlama 1.1B | 4-8GB | Good | Very Fast |

## Best Practices

1. **Use separate llamafiles** for embedding and chat to optimize each for their specific task
2. **Configure appropriate context lengths** based on your document sizes
3. **Tune batch sizes** for your hardware and workload
4. **Monitor memory usage** and adjust quantization levels as needed
5. **Use task-specific prefixes** for embedding models (especially Nomic)
6. **Implement proper error handling** and fallback mechanisms
7. **Cache frequently used embeddings** to improve performance

This setup provides a production-ready, scalable RAG system using llamafiles that can handle document ingestion, vector search, and conversational AI locally without external dependencies.

---

## Attribution & Support

**Created by Luke Steuber**
- **Website**: [lukesteuber.com](https://lukesteuber.com)
- **Professional**: [assisted.site](https://assisted.site)
- **Contact**: luke@lukesteuber.com
- **Social**: [@lukesteuber.com](https://bsky.app/profile/lukesteuber.com) on Bluesky
- **LinkedIn**: [LinkedIn Profile](https://www.linkedin.com/in/lukesteuber/)
- **Support**: [Tip Jar](https://usefulai.lemonsqueezy.com/buy/bf6ce1bd-85f5-4a09-ba10-191a670f74af)
- **Newsletter**: [lukesteuber.substack.com](https://lukesteuber.substack.com/)
- **Code**: [GitHub @lukeslp](https://github.com/lukeslp)
- **Models**: [Ollama coolhand](https://ollama.com/coolhand)
- **Pip**: [lukesteuber](https://pypi.org/user/lukesteuber/)

**MIT License** - see [LICENSE](../LICENSE) file for complete details. 