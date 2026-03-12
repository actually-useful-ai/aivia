/**
 * Streaming Chat Implementation
 * A reusable implementation for streaming chat responses from an AI model.
 * 
 * Features:
 * - Streaming response handling
 * - Markdown rendering
 * - Error handling
 * - Loading states
 * 
 * @requires markdownit
 * @requires highlight.js
 */

class StreamingChat {
  constructor(config = {}) {
    this.apiBaseUrl = config.apiBaseUrl || process.env.API_BASE_URL;
    this.apiKey = config.apiKey || process.env.API_KEY;
    this.model = config.model || process.env.DEFAULT_MODEL;
    this.md = window.markdownit();
    this.messages = [];
  }

  /**
   * Process markdown content with syntax highlighting
   * @param {string} content - Raw markdown content
   * @returns {string} - Processed HTML
   */
  processMessageContent(content) {
    const parsedContent = this.md.render(content);
    const container = document.createElement("div");
    container.className = "markdown-body message-content";
    container.innerHTML = parsedContent;

    // Apply syntax highlighting
    container.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });

    return container.outerHTML;
  }

  /**
   * Send a message and handle streaming response
   * @param {string} content - User message content
   * @param {Object} options - Additional options
   * @returns {Promise<void>}
   */
  async sendMessage(content, options = {}) {
    if (!content?.trim()) return;

    this.messages.push({
      role: "user",
      content: content
    });

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          messages: this.messages,
          model: this.model,
          stream: true,
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(`HTTP error! status: ${response.status}${errorData ? ' - ' + JSON.stringify(errorData) : ''}`);
      }

      let fullContent = "";
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.trim() === '' || line === 'data: [DONE]') continue;
          if (line.startsWith('data: ')) {
            try {
              const parsed = JSON.parse(line.slice(6));
              const content = parsed.choices?.[0]?.delta?.content;
              if (content) {
                fullContent += content;
                if (options.onChunk) {
                  options.onChunk(content, fullContent);
                }
              }
            } catch (e) {
              console.warn('Error parsing chunk:', e);
            }
          }
        }
      }

      this.messages.push({
        role: "assistant",
        content: fullContent
      });

      if (options.onComplete) {
        options.onComplete(fullContent);
      }

    } catch (error) {
      console.error("Error:", error);
      if (options.onError) {
        options.onError(error);
      }
      throw error;
    }
  }
}

// Usage example:
/*
const chat = new StreamingChat({
  apiBaseUrl: 'https://your-api.com',
  apiKey: 'your-api-key',
  model: 'your-model'
});

await chat.sendMessage("Hello!", {
  onChunk: (chunk, fullContent) => {
    // Handle each chunk of the response
    console.log('New chunk:', chunk);
  },
  onComplete: (fullContent) => {
    // Handle complete response
    console.log('Complete response:', fullContent);
  },
  onError: (error) => {
    // Handle errors
    console.error('Chat error:', error);
  }
});
*/ 