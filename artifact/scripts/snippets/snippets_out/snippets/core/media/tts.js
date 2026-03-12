/**
 * Text-to-Speech Processing
 */

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