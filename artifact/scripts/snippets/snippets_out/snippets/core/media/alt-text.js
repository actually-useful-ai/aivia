/**
 * Alt Text Generation
 */

export const AltTextGenerator = {
    // Prompt templates for different alt text styles
    promptTemplates: {
        base: "Generate concise, descriptive alt text for this image that captures its essential details and context.",
        shorter: "Generate brief alt text under 300 characters, focusing on critical details only.",
        longer: "Generate detailed alt text (800+ characters) with comprehensive visual description.",
        enhance: "Use additional context and research to generate detailed alt text, including artist/source attribution.",
        retry: "Generate alternative alt text with a different perspective or focus."
    },

    // Build prompt based on command
    buildPrompt(command = "") {
        let prompt = this.promptTemplates.base;
        
        if (command && this.promptTemplates[command]) {
            prompt = this.promptTemplates[command];
        }
        
        return prompt;
    },

    // Process media file for alt text generation
    async processMedia(file, options = {}) {
        try {
            MediaTypes.validateFile(file);
            
            // Convert file to base64 or appropriate format
            const fileData = await this.prepareFileData(file);
            
            // Generate alt text based on options
            const altText = await this.generateAltText(fileData, options);
            
            return {
                success: true,
                altText,
                file: {
                    name: file.name,
                    type: file.type,
                    size: file.size
                }
            };
        } catch (error) {
            console.error('Media processing error:', error);
            return {
                success: false,
                error: error.message,
                file: file ? {
                    name: file.name,
                    type: file.type,
                    size: file.size
                } : null
            };
        }
    },

    // Prepare file data for processing
    async prepareFileData(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('File reading failed'));
            reader.readAsDataURL(file);
        });
    },

    // Generate alt text using API
    async generateAltText(fileData, options = {}) {
        const response = await fetch(`${options.apiUrl || '/api/alt-text'}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: fileData,
                command: options.command || 'base',
                prompt: this.buildPrompt(options.command)
            })
        });

        if (!response.ok) {
            throw new Error('Alt text generation failed');
        }

        return await response.json();
    }
}; 