/**
 * Alt text generation utilities
 */

/**
 * System prompt for alt text generation
 */
export const ALT_TEXT_SYSTEM_PROMPT = `You're an Alt Text Specialist, dedicated to creating precise and accessible alt text for digital images, especially memes. Your primary goal is to ensure visually impaired individuals can engage with imagery by providing concise, accurate, and ethically-minded descriptions.

Create Alt Text
- **Depict essential visuals and visible text accurately.**
- **Avoid adding social-emotional context or narrative interpretations unless specifically requested.**
- **Refrain from speculating on artists' intentions.**
- **Avoid prepending with "Alt text:" for direct usability.**
- **Maintain clarity and consistency for all descriptions, including direct image links.**
- **Character limit:** All descriptions must be under 1000 characters.`;

/**
 * Analyzes an image and generates alt text using the specified model
 * @param {string} base64Content - Base64 encoded image content
 * @param {string} model - The model to use for analysis
 * @param {string} apiBaseUrl - The base URL for the API
 * @returns {Promise<Response>} The API response
 */
export const analyzeImage = async (base64Content, model, apiBaseUrl) => {
    try {
        const messages = [{
            role: "system",
            content: ALT_TEXT_SYSTEM_PROMPT
        }, {
            role: "user",
            content: "Please provide alt text for this image.",
            images: base64Content ? [base64Content] : undefined
        }];

        const response = await makeApiCall(messages, base64Content, model, apiBaseUrl);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error (${response.status}): ${errorText}`);
        }

        return response;
    } catch (error) {
        console.error('Error analyzing image:', error);
        throw error;
    }
}; 