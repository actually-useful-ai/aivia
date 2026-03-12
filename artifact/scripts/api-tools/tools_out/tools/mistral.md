# Mistral AI Tool Documentation

## Overview
The Mistral tool provides integration with Mistral's large language models, offering advanced natural language processing capabilities. It supports both chat-based interactions and direct completions, with features for context management and response streaming.

## Required Credentials
```python
MISTRAL_API_KEY="your_mistral_api_key"  # Required for all operations
```

## Available Models
- `mistral-tiny`: Fast, efficient model for simple tasks
- `mistral-small`: Balanced performance and capability
- `mistral-medium`: Advanced reasoning and generation
- `mistral-large`: Most capable model for complex tasks

## Input Parameters

### Required Parameters
- `prompt` (str): The input text or prompt
- `model` (str): Model identifier (default: 'mistral-small')

### Optional Parameters
```python
{
    "temperature": float,      # 0.0-1.0, default: 0.7
    "max_tokens": int,        # default: 1000
    "top_p": float,          # 0.0-1.0, default: 0.95
    "stream": bool,          # Enable streaming, default: False
    "safe_mode": bool,       # Enable content filtering, default: True
    "random_seed": int,      # For reproducible results
    "stop_sequences": list   # Custom stop sequences
}
```

## Output Format

### Chat Response
```json
{
    "id": "response_id",
    "model": "model_name",
    "created_at": "ISO datetime",
    "response": {
        "role": "assistant",
        "content": "Generated response",
        "finish_reason": "stop|length|content_filter"
    },
    "usage": {
        "prompt_tokens": 123,
        "completion_tokens": 456,
        "total_tokens": 579
    }
}
```

### Streaming Response
```python
for chunk in response.iter_lines():
    {
        "id": "chunk_id",
        "content": "Partial response",
        "finish_reason": null|"stop"|"length"
    }
```

## Rate Limits
- Requests per minute: Varies by subscription
- Tokens per minute: Varies by model and subscription
- Concurrent requests: Based on subscription tier

## Error Handling
```python
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "param": "Parameter causing error",
        "type": "invalid_request|api_error|rate_limit"
    }
}
```

Common error codes:
- `INVALID_API_KEY`
- `RATE_LIMIT_EXCEEDED`
- `CONTEXT_LENGTH_EXCEEDED`
- `CONTENT_POLICY_VIOLATION`
- `MODEL_UNAVAILABLE`

## Example Usage

### Basic Chat
```python
from tools.mistral import MistralAI

mistral = MistralAI()
response = mistral.chat("Explain quantum computing")
print(response['response']['content'])
```

### Advanced Usage
```python
response = mistral.generate(
    prompt="Write a technical analysis of...",
    model="mistral-large",
    temperature=0.3,
    max_tokens=2000,
    stream=True,
    safe_mode=True
)
```

### System Messages
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "Help me with..."}
]
response = mistral.chat_messages(messages)
```

## Common Applications

### Content Generation
1. Technical writing
2. Creative writing
3. Code generation
4. Documentation creation

### Analysis Tasks
1. Text summarization
2. Sentiment analysis
3. Content classification
4. Data extraction

### Conversational AI
1. Customer support
2. Educational tutoring
3. Expert systems
4. Interactive assistants

## Integration Examples

### With Web Search
```python
from tools.web_search import WebSearch
from tools.mistral import MistralAI

def research_and_analyze(topic):
    # Get search results
    search_results = WebSearch().search(topic)
    
    # Format context
    context = "\n".join([r['snippet'] for r in search_results])
    
    # Analyze with Mistral
    prompt = f"Based on this information:\n{context}\n\nProvide an analysis of {topic}"
    analysis = MistralAI().generate(prompt)
    return analysis
```

### With Code Execution
```python
from tools.mistral import MistralAI
from tools.runCode import CodeExecutor

def generate_and_test_code(task):
    # Generate code
    prompt = f"Write Python code to {task}"
    code = MistralAI().generate(prompt)
    
    # Test the code
    result = CodeExecutor().run(code)
    return result
```

## Best Practices

### Prompt Engineering
1. Be specific and clear
2. Provide context
3. Use system messages
4. Include examples
5. Set appropriate constraints

### Model Selection
1. Match model to task complexity
2. Consider response time needs
3. Balance cost and performance
4. Use smallest sufficient model

### Response Handling
1. Implement retry logic
2. Handle streaming properly
3. Validate outputs
4. Monitor token usage

## Performance Optimization

### Token Management
1. Compress input when possible
2. Use efficient encodings
3. Implement context windows
4. Track token usage

### Cost Optimization
1. Cache common responses
2. Use streaming for long outputs
3. Batch similar requests
4. Monitor API usage

### Quality Control
1. Implement content filtering
2. Validate outputs
3. Handle edge cases
4. Monitor response quality

## Troubleshooting

### Common Issues
1. Token limit exceeded
   - Solution: Chunk input or summarize
2. Rate limiting
   - Solution: Implement backoff
3. Content filtering triggers
   - Solution: Adjust prompts
4. Response quality
   - Solution: Refine prompts or adjust parameters

### Monitoring
1. Track usage metrics
2. Monitor error rates
3. Log response times
4. Analyze output quality 