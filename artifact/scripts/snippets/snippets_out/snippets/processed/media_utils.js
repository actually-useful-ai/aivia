/**
 * Media Processing Utilities
 * Consolidated from multiple files
 */

// Media Type Support
export const MediaTypes = {
    // Supported media formats
    supportedTypes: [
        // Image Formats
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'image/heic', 'image/heif', 'image/avif', 'image/tiff', 'image/bmp',
        'image/x-icon', 'image/vnd.microsoft.icon', 'image/svg+xml',
        'image/vnd.adobe.photoshop', 'image/x-adobe-dng', 'image/x-canon-cr2',
        'image/x-nikon-nef', 'image/x-sony-arw', 'image/x-fuji-raf',
        'image/x-olympus-orf', 'image/x-panasonic-rw2', 'image/x-rgb',
        'image/x-portable-pixmap', 'image/x-portable-graymap',
        'image/x-portable-bitmap',
        // Video Formats
        'video/mp4', 'video/quicktime', 'video/webm', 'video/x-msvideo',
        'video/x-flv', 'video/x-ms-wmv', 'video/x-matroska', 'video/3gpp',
        'video/x-m4v', 'video/x-ms-asf', 'video/x-mpegURL', 'video/x-ms-vob',
        'video/x-ms-tmp', 'video/x-mpeg', 'video/mp2t',
        // Generic
        'application/octet-stream'
    ],

    isSupported(fileType) {
        return this.supportedTypes.includes(fileType) || 
               fileType.startsWith('image/') || 
               fileType.startsWith('video/');
    },

    validateFile(file) {
        if (!file) {
            throw new Error('No file provided');
        }
        if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
            throw new Error('Unsupported file type');
        }
        if (file.size > 20 * 1024 * 1024) {
            throw new Error('File size exceeds 20MB limit');
        }
        if (!this.isSupported(file.type)) {
            throw new Error('File format not supported');
        }
        return true;
    }
};

// Alt Text Generation
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

// Text-to-Speech Processing
export const TTSProcessor = {
    async generateTTS(text, options = {}) {
        try {
            const response = await fetch(`${options.apiUrl || '/api/tts'}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify({
                    text,
                    voice: options.voice || 'default',
                    speed: options.speed || 1.0,
                    pitch: options.pitch || 1.0
                })
            });

            if (!response.ok) {
                throw new Error('TTS generation failed');
            }

            const audioUrl = await this.processStreamResponse(response);
            return this.createAudioElement(audioUrl);
        } catch (error) {
            console.error('TTS generation error:', error);
            throw error;
        }
    },

    async processStreamResponse(response) {
        const reader = response.body.getReader();
        let content = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = new TextDecoder().decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data:')) {
                    const data = JSON.parse(line.slice(5).trim());
                    if (data.type === 'delta') {
                        content += data.content;
                    }
                }
            }
        }

        const urlMatch = content.match(/\((https?:\/\/[^\s]+)\)/);
        if (!urlMatch) {
            throw new Error('No audio URL found in response');
        }

        return urlMatch[1];
    },

    createAudioElement(audioUrl) {
        const container = document.createElement('div');
        container.className = 'audio-container';
        container.setAttribute('role', 'region');
        container.setAttribute('aria-label', 'Audio Player');

        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = audioUrl;
        audio.setAttribute('aria-label', 'Text-to-Speech Audio');
        container.appendChild(audio);

        const downloadLink = document.createElement('a');
        downloadLink.href = audioUrl;
        downloadLink.download = 'tts_output.mp3';
        downloadLink.textContent = 'Download Audio';
        downloadLink.className = 'download-link';
        downloadLink.setAttribute('aria-label', 'Download audio file');
        container.appendChild(downloadLink);

        return container;
    }
}; 