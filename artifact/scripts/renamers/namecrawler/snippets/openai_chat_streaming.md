# OpenAI Chat Completion Streaming Example

```python
import openai

openai.api_key = "YOUR_API_KEY"  # Replace with your key

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Describe the file"}],
    stream=True,
)

for chunk in response:
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta.content, end="", flush=True)
```

This snippet demonstrates how to stream chat completion responses line-by-line.
