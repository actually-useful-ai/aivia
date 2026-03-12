/**
 * Conversation Summary
 */

export const ConversationSummarizer = {
    /**
     * System prompt for conversation analysis
     */
    systemPrompt: `You are a conversation analysis assistant. Analyze the following exchange and respond ONLY with a JSON object in this exact format, ensuring to include relevant items in each array (do not return empty arrays unless there is truly nothing to report):

{
  "summary": [{"point": "Main points from the conversation", "context": "Additional context or details"}],
  "todos": [{"task": "Any action items or tasks mentioned", "priority": "high|medium|low", "context": "Task details"}],
  "references": [{"title": "Names of references", "url": "URLs if any", "context": "How it was referenced"}],
  "code": [{"language": "Programming language", "snippet": "Code snippets discussed", "description": "What the code does"}],
  "embedded": [{"type": "Type of content", "content": "Content details", "description": "Content context"}],
  "questions": [{"question": "Questions raised", "context": "Question context"}]
}

Important: Analyze the conversation thoroughly and include all relevant information. Do not return empty arrays unless that category truly has no relevant content.`,

    /**
     * Summarizes a conversation
     * @param {string} userMessage - The user's message
     * @param {string} assistantResponse - The assistant's response
     * @param {string} apiUrl - The API URL
     * @returns {Promise<Object>} The summary data
     */
    async summarizeConversation(userMessage, assistantResponse, apiUrl) {
        console.log("[Summary] Analyzing conversation");
        const conversationText = `User: ${userMessage}\nAssistant: ${assistantResponse}`;

        const summaryPayload = {
            message: conversationText,
            system_prompt: this.systemPrompt,
            bot_id: "7432075476698546182",
            user_id: `summary_${Date.now()}`,
            conversation_id: `summary_${Date.now()}`
        };

        try {
            const response = await fetch(`${apiUrl}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                body: JSON.stringify(summaryPayload)
            });

            if (!response.ok) {
                throw new Error(`Summary request failed: ${response.status}`);
            }

            return await this.processStreamResponse(response);
        } catch (error) {
            console.error("[Summary] Error:", error);
            throw error;
        }
    },

    /**
     * Processes the stream response
     * @param {Response} response - The response object
     * @returns {Promise<Object>} The processed data
     */
    async processStreamResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let accumulatedData = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");

            for (const line of lines) {
                if (line.startsWith("data:")) {
                    const eventData = line.slice(5).trim();
                    if (!eventData) continue;

                    try {
                        const data = JSON.parse(eventData);
                        if (data.type === "delta" && data.content) {
                            accumulatedData += data.content;
                        } else if (data.type === "complete") {
                            const jsonMatch = accumulatedData.match(/\{[\s\S]*\}/);
                            if (jsonMatch) {
                                return JSON.parse(jsonMatch[0]);
                            }
                            throw new Error("No valid JSON found in response");
                        }
                    } catch (e) {
                        console.error("[Summary] Stream processing error:", e);
                    }
                }
            }
        }
        throw new Error("Stream ended without complete signal");
    }
}; 