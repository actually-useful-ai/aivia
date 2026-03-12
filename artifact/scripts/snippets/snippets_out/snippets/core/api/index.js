/**
 * API utilities
 */

/**
 * Default model for API calls
 */
export const DEFAULT_MODEL = "coolhand/impossible_alt:13b";

/**
 * Base URL for API endpoints
 */
export const API_BASE_URL = "https://7584e4c6571c.ngrok.app/api";

/**
 * Makes an API call with the specified parameters
 * @param {Array} messages - The messages to send
 * @param {string} base64Image - Base64 encoded image data
 * @param {string} model - The model to use
 * @param {string} apiBaseUrl - The base URL for the API
 * @returns {Promise<Response>} The API response
 */
export const makeApiCall = async (messages, base64Image, model, apiBaseUrl) => {
    const requestBody = {
        model,
        messages,
        stream: true
    };

    if (base64Image) {
        requestBody.messages[requestBody.messages.length - 1].images = [base64Image];
    }

    console.log("API Request details:", {
        url: `${apiBaseUrl}/chat`,
        body: { 
            ...requestBody, 
            messages: requestBody.messages,
            images: requestBody.images ? ['[Image Data]'] : undefined 
        }
    });

    return fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    });
};

/**
 * Processes a streamed response from the API
 * @param {Response} response - The API response to process
 * @param {Object} callbacks - Callback functions for different events
 * @returns {Promise<Object>} The processed response data
 */
export const processStreamedResponse = async (response, {
    onContent = () => {},
    onDone = () => {},
    onError = () => {}
} = {}) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullContent = "";
    let totalTokens = 0;

    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.trim() === '') continue;

                try {
                    const data = JSON.parse(line);
                    
                    if (data.message?.content) {
                        fullContent += data.message.content;
                        onContent(data.message.content);
                    }

                    if (data.done) {
                        totalTokens = data.prompt_eval_count + data.eval_count;
                        onDone({
                            fullContent,
                            totalTokens,
                            messages: [{
                                role: "assistant",
                                content: fullContent
                            }]
                        });
                    }
                } catch (error) {
                    console.warn("Error parsing line:", line, error);
                    continue;
                }
            }
        }
    } catch (error) {
        onError(error);
        throw error;
    }

    return { fullContent, totalTokens };
}; 