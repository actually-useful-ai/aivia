# X.AI Unified Tool

A comprehensive toolkit that interfaces with the X.AI (Grok) API to provide multiple AI functionalities in a unified interface. This tool combines multiple features into a single script to make it easier to use X.AI's powerful models.

## Features

- **Interactive Chat:** Have natural conversations with Grok models
- **Vision Support:** Analyze images and get detailed descriptions
- **Alt Text Generation:** Generate comprehensive alt text for images in a gallery
- **ArXiv Paper Analysis:** Process academic papers from ArXiv and get summaries or answers to specific questions
- **Multiple Models:** Choose from different Grok models based on your needs
- **Streaming Responses:** Experience real-time responses with streaming output

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenAI Python package (for X.AI API compatibility)
- Pillow (optional, for image handling)
- Requests (for HTTP requests)

### Setup

1. Install the required packages:

```bash
pip install openai requests pillow
```

2. Set your X.AI API key as an environment variable:

```bash
export XAI_API_KEY="your-xai-api-key"
```

## Usage

The tool offers multiple modes of operation:

### Interactive Chat Mode (Default)

```bash
python xai_unified.py
```

This will:
1. List available X.AI models
2. Let you select a model
3. Start an interactive chat session
4. Offer options to include images in the conversation

### Alt Text Generation Mode

```bash
python xai_unified.py --alt-text --input-file your-gallery.js --output-file output.js
```

This mode processes a JavaScript file containing an array of image objects, generating comprehensive alt text for each image. Results are cached to avoid regenerating alt text for the same images.

### ArXiv Paper Processing

```bash
python xai_unified.py --arxiv --paper-id 2307.09288 --query "What are the key innovations in this paper?"
```

This mode processes an ArXiv paper and generates a response based on your query.

## Command-Line Arguments

The tool accepts various command-line arguments to customize its behavior:

### General Options

- `--api-key KEY`: Specify the X.AI API key (overrides environment variable)

### Mode Selection

- `--chat`: Explicitly enter chat mode (default)
- `--alt-text`: Generate alt text for images
- `--arxiv`: Process ArXiv papers

### Chat Options

- `--model MODEL_ID`: Specify a particular model to use
- `--system-prompt PROMPT`: Set a custom system prompt for the conversation
- `--temperature TEMP`: Set the temperature for response generation (0.0-1.0)
- `--image PATH_OR_URL`: Include an image in the conversation

### Alt Text Options

- `--input-file FILE`: Input JavaScript file containing image data
- `--output-file FILE`: Output JavaScript file for updated image data

### ArXiv Options

- `--paper-id ID`: ArXiv paper ID to analyze
- `--query QUERY`: Specific question about the paper

## Examples

### Chat with a Specific Model

```bash
python xai_unified.py --model grok-2-vision-latest
```

### Ask About an Image

```bash
python xai_unified.py --image https://example.com/image.jpg --model grok-2-vision-latest
```

### Generate Alt Text for Gallery Images

```bash
python xai_unified.py --alt-text
```

### Analyze an ArXiv Paper

```bash
python xai_unified.py --arxiv --paper-id 2307.09288
```

## File Format for Alt Text Generation

The script expects an image gallery file in JavaScript format with this structure:

```javascript
const galleryImages = [
  {
    "id": "image1",
    "url": "https://example.com/image1.jpg",
    "description": "",
    "alt_text": ""
  },
  // More images...
];
```

The script will:
1. Back up the original file
2. Generate alt text for each image
3. Update the `description` and `alt_text` fields
4. Write the updated gallery to a new file
5. Maintain a cache to avoid regenerating alt text for the same images

## Extending the Tool

The `XAIUnified` class can be imported and used in your own Python scripts. Here's a simple example:

```python
from xai_unified import XAIUnified

# Initialize the client
xai = XAIUnified(api_key="your-xai-api-key")

# Generate alt text for an image
alt_text = xai.generate_alt_text("https://example.com/image.jpg")
print(alt_text)

# Chat with Grok
for chunk in xai.stream_chat_response("Tell me about quantum computing"):
    print(chunk, end="", flush=True)
```

## Notes

- The API key is sensitive information. Always use environment variables or secure methods to provide it, especially in production environments.
- This tool combines functionality from multiple scripts in the to_strip directory, providing a unified interface for X.AI operations.
- Streaming responses provide a more interactive experience but require handling text chunks as they arrive.

## Accessibility Features

This tool was designed with accessibility in mind, particularly the alt text generation feature which produces detailed descriptions for images that can be used for screen readers and other assistive technologies. 