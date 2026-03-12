/**
 * Stream Content Management
 */

export const StreamManager = {
    setupStream(config) {
        const {
            onDelta = () => {},
            onComplete = () => {},
            onError = console.error,
            decoder = new TextDecoder()
        } = config;

        return {
            async processStream(reader) {
                try {
                    while (true) {
                        const { value, done } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value, { stream: true });
                        const lines = chunk.split('\n');

                        for (const line of lines) {
                            if (line.startsWith('data:')) {
                                try {
                                    const data = JSON.parse(line.slice(5));
                                    if (data.type === 'delta') {
                                        onDelta(data);
                                    } else if (data.type === 'complete') {
                                        onComplete(data);
                                    }
                                } catch (error) {
                                    onError('Error parsing stream:', error);
                                }
                            }
                        }
                    }
                } catch (error) {
                    onError('Stream processing error:', error);
                }
            }
        };
    }
}; 