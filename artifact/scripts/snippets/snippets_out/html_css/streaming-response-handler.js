/**
 * streaming-response-handler.js
 * Handles streaming response processing from different LLM providers
 * 
 * This module demonstrates how to handle streaming responses from different AI model
 * providers, including parsing tokens, updating the UI, and handling errors.
 */

import { processMessageContent } from './chain-of-thought-processor.js';
import { createThoughtBubble } from './thought-bubble.js';

/**
 * Process streaming response from a model provider
 * @param {Response} response - The response object from fetch API
 * @param {Object} state - The application state
 * @param {Function} updateUI - Function to update the UI with new content
 * @param {Object} md - The markdown-it instance
 * @returns {Promise<void>}
 */
export async function processStreamingResponse(response, state, updateUI, md) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let streamedText = '';
    let lastThoughtUpdateTime = 0;
    let hasThoughtTags = false;
    
    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            
            // Process chunks based on model provider format
            const modelProvider = state.currentModel?.provider || detectProviderFromContent(buffer);
            
            // Process the buffer based on the model provider format
            const { processed, remaining, thoughts } = processBuffer(buffer, modelProvider);
            
            if (processed) {
                streamedText += processed;
                buffer = remaining || '';
                
                // Update UI with the processed content
                updateUI(streamedText);
                
                // Handle thought processing if available
                if (thoughts && thoughts.length > 0) {
                    hasThoughtTags = true;
                    const now = Date.now();
                    
                    // Limit thought bubble updates to prevent too many DOM updates
                    if (now - lastThoughtUpdateTime > 300) {
                        lastThoughtUpdateTime = now;
                        
                        // Create thought bubbles for each thought
                        thoughts.forEach(thought => {
                            if (thought.trim()) {
                                createThoughtBubble(thought, md);
                            }
                        });
                    }
                }
            }
        }
        
        // Process any remaining buffer
        if (buffer) {
            streamedText += buffer;
            updateUI(streamedText);
        }
        
        // Process final message content with potential thought tags
        if (hasThoughtTags) {
            const processedContent = processMessageContent(streamedText, md);
            updateUI(processedContent, true);
        }
        
        return streamedText;
    } catch (error) {
        console.error('Error processing stream:', error);
        throw error;
    }
}

/**
 * Detect provider from content pattern
 * @param {string} content - The content to analyze
 * @returns {string} - The detected provider
 */
function detectProviderFromContent(content) {
    if (content.includes('"model":"mistral') || content.includes('"choices":[{"delta":')) {
        return 'mistral';
    } else if (content.includes('<|thinking|>') || content.includes('<|begin_of_thought|>')) {
        return 'deepseek';
    } else if (content.includes('data: [DONE]')) {
        return 'openai';
    } else {
        return 'unknown';
    }
}

/**
 * Process buffer based on model provider format
 * @param {string} buffer - The current buffer
 * @param {string} provider - The model provider
 * @returns {Object} - The processed text, remaining buffer, and thoughts
 */
function processBuffer(buffer, provider) {
    switch (provider) {
        case 'mistral':
            return processMistralBuffer(buffer);
        case 'deepseek':
            return processDeepseekBuffer(buffer);
        case 'openai':
            return processOpenAIBuffer(buffer);
        case 'anthropic':
            return processAnthropicBuffer(buffer);
        default:
            // Default line-by-line processing
            return processGenericBuffer(buffer);
    }
}

/**
 * Process Mistral streaming format
 * @param {string} buffer - The current buffer
 * @returns {Object} - The processed text, remaining buffer, and thoughts
 */
function processMistralBuffer(buffer) {
    let processed = '';
    let thoughts = [];
    
    // Split by data: to get each chunk
    const chunks = buffer.split('data: ');
    
    // Process all chunks except the last one (which might be incomplete)
    const completeChunks = chunks.slice(0, -1);
    const remaining = 'data: ' + chunks[chunks.length - 1];
    
    for (const chunk of completeChunks) {
        if (!chunk.trim() || chunk.includes('[DONE]')) continue;
        
        try {
            const data = JSON.parse(chunk);
            
            if (data.choices && data.choices[0]?.delta?.content) {
                const content = data.choices[0].delta.content;
                processed += content;
                
                // Extract thoughts if present in tags
                if (content.includes('<|thinking|>') || content.includes('<|begin_of_thought|>')) {
                    const thoughtMatch = content.match(/<\|thinking\|>(.*?)<\|\/thinking\|>/s) || 
                                       content.match(/<\|begin_of_thought\|>(.*?)<\|end_of_thought\|>/s);
                    
                    if (thoughtMatch && thoughtMatch[1]) {
                        thoughts.push(thoughtMatch[1]);
                    }
                }
            }
        } catch (e) {
            console.warn('Could not parse Mistral chunk:', chunk, e);
        }
    }
    
    return { processed, remaining, thoughts };
}

/**
 * Process Deepseek streaming format (with thinking tags)
 * @param {string} buffer - The current buffer
 * @returns {Object} - The processed text, remaining buffer, and thoughts
 */
function processDeepseekBuffer(buffer) {
    let processed = '';
    let thoughts = [];
    let remaining = '';
    
    // Handle the case where we're inside a thought block
    const thoughtStartIndex = buffer.lastIndexOf('<|thinking|>');
    const thoughtEndIndex = buffer.lastIndexOf('<|/thinking|>');
    
    if (thoughtStartIndex > thoughtEndIndex) {
        // We're in the middle of a thought, extract known part
        remaining = buffer.substring(thoughtStartIndex);
        processed = buffer.substring(0, thoughtStartIndex);
    } else {
        // Process all complete thought sections
        const thoughtPattern = /<\|thinking\|>(.*?)<\|\/thinking\|>/gs;
        let match;
        
        while ((match = thoughtPattern.exec(buffer)) !== null) {
            // Extract and add to thoughts
            if (match[1]) {
                thoughts.push(match[1]);
            }
        }
        
        // For streaming, we need to handle partial thoughts at the end
        processed = buffer;
    }
    
    return { processed, remaining, thoughts };
}

/**
 * Process OpenAI streaming format
 * @param {string} buffer - The current buffer
 * @returns {Object} - The processed text, remaining buffer, and thoughts
 */
function processOpenAIBuffer(buffer) {
    let processed = '';
    const chunks = buffer.split('data: ');
    
    // Process all chunks except the last one (which might be incomplete)
    const completeChunks = chunks.slice(0, -1);
    const remaining = chunks.length > 0 ? 'data: ' + chunks[chunks.length - 1] : '';
    
    for (const chunk of completeChunks) {
        if (!chunk.trim() || chunk.includes('[DONE]')) continue;
        
        try {
            const data = JSON.parse(chunk);
            if (data.choices && data.choices[0]?.delta?.content) {
                processed += data.choices[0].delta.content;
            }
        } catch (e) {
            console.warn('Could not parse OpenAI chunk:', chunk, e);
        }
    }
    
    return { processed, remaining, thoughts: [] };
}

/**
 * Process Anthropic streaming format
 * @param {string} buffer - The current buffer
 * @returns {Object} - The processed text, remaining buffer, and thoughts
 */
function processAnthropicBuffer(buffer) {
    let processed = '';
    const events = buffer.split('\n\n');
    
    // Process all events except the last one (which might be incomplete)
    const completeEvents = events.slice(0, -1);
    const remaining = events.length > 0 ? events[events.length - 1] : '';
    
    for (const event of completeEvents) {
        const lines = event.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.substring(6);
                if (data === '[DONE]') continue;
                
                try {
                    const parsed = JSON.parse(data);
                    if (parsed.type === 'content_block_delta' && parsed.delta?.text) {
                        processed += parsed.delta.text;
                    }
                } catch (e) {
                    console.warn('Could not parse Anthropic data:', data, e);
                }
            }
        }
    }
    
    return { processed, remaining, thoughts: [] };
}

/**
 * Process generic line-by-line buffer for unknown formats
 * @param {string} buffer - The current buffer
 * @returns {Object} - The processed text, remaining buffer, and thoughts
 */
function processGenericBuffer(buffer) {
    // Simple line-by-line processing
    const lines = buffer.split('\n');
    const processedLines = lines.slice(0, -1); // All lines except the potentially incomplete last line
    const processed = processedLines.join('\n');
    const remaining = lines.length > 0 ? lines[lines.length - 1] : '';
    
    return { processed, remaining, thoughts: [] };
}

/**
 * Create the loading UI for a streaming response
 * @returns {HTMLElement} - The loading container element
 */
export function createLoadingUI() {
    const loadingContainer = document.createElement('div');
    loadingContainer.id = 'loadingContainer';
    loadingContainer.className = 'loading-container';
    
    const loadingGif = document.createElement('div');
    loadingGif.className = 'loading-gif';
    
    // Three dot animation
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'loading-dot';
        loadingGif.appendChild(dot);
    }
    
    loadingContainer.appendChild(loadingGif);
    
    // Hidden by default
    loadingContainer.style.display = 'none';
    
    return loadingContainer;
}

/**
 * Example CSS for loading animation
 * Add this to your CSS file
 */
/*
.loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
}

.loading-gif {
    display: flex;
    align-items: center;
    justify-content: center;
}

.loading-dot {
    width: 8px;
    height: 8px;
    margin: 0 3px;
    background-color: #4285f4;
    border-radius: 50%;
    animation: dot-bounce 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
    animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes dot-bounce {
    0%, 80%, 100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1);
    }
}
*/ 