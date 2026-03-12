/**
 * Prompt Management
 */

export const PromptManager = {
    /**
     * Combines multiple prompts with proper formatting
     * @param {Array<string>} prompts - Array of prompts to combine
     * @param {string} separator - Separator between prompts
     * @returns {string} The combined prompt
     */
    combinePrompts(prompts, separator = "\n\n") {
        return prompts.filter(Boolean).join(separator);
    },

    /**
     * Adds specific constraints to a prompt
     * @param {string} prompt - The base prompt
     * @param {Object} constraints - Constraint key-value pairs
     * @returns {string} The prompt with constraints
     */
    addConstraints(prompt, constraints) {
        const constraintText = Object.entries(constraints)
            .map(([key, value]) => `${key}: ${value}`)
            .join("\n");
        return `${prompt}\n\nConstraints:\n${constraintText}`;
    },

    /**
     * Creates a structured prompt with multiple sections
     * @param {Object} sections - Section key-value pairs
     * @returns {string} The structured prompt
     */
    createStructuredPrompt(sections) {
        return Object.entries(sections)
            .map(([heading, content]) => `${heading}:\n${content}`)
            .join("\n\n");
    },

    /**
     * Adds examples to a prompt
     * @param {string} prompt - The base prompt
     * @param {Array<Object>} examples - Array of example objects
     * @returns {string} The prompt with examples
     */
    addExamples(prompt, examples) {
        const exampleText = examples
            .map(ex => `Input: ${ex.input}\nOutput: ${ex.output}`)
            .join("\n\n");
        return `${prompt}\n\nExamples:\n${exampleText}`;
    },

    /**
     * Creates a prompt with specific formatting requirements
     * @param {string} prompt - The base prompt
     * @param {string} format - The required format
     * @returns {string} The formatted prompt
     */
    withFormatting(prompt, format) {
        return `${prompt}\n\nRequired Format:\n${format}`;
    }
}; 