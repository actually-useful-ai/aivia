/**
 * Conversation and Summary Utilities
 * Extracted from from_utils.js
 */

// Conversation Export
export const ConversationExporter = {
    downloadConversation(messages, botName = "Assistant") {
        console.log("[Export] Starting conversation export...");
        const now = new Date();
        const dateTime = now.toLocaleString();

        const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Conversation Download - ${dateTime}</title>
    <style>
        body {
            font-family: 'Open Sans', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            color: #2c3e50;
            line-height: 1.6;
        }
        .message {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }
        .user-message {
            background-color: #f5f5f5;
            margin-left: 20%;
        }
        .bot-message {
            background-color: #e8f4f8;
            margin-right: 20%;
        }
        .system-message {
            background-color: #fff3e0;
            text-align: center;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Conversation with ${botName} - ${dateTime}</h1>
    <div class="conversation">
        ${Array.from(messages)
            .map((msg) => {
                const className = msg.className.split(" ")[1];
                const content = msg.querySelector(".message-content")
                    ? msg.querySelector(".message-content").innerHTML
                    : msg.innerHTML;
                return `<div class="message ${className}">${content}</div>`;
            })
            .join("\n")}
    </div>
</body>
</html>`;

        const blob = new Blob([htmlContent], { type: "text/html" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `conversation-${now.toISOString().split("T")[0]}.html`;
        a.click();
        window.URL.revokeObjectURL(url);
        console.log("[Export] Export complete");
    }
};

// Conversation Summary
export const ConversationSummarizer = {
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

// Summary UI Manager
export const SummaryUIManager = {
    showLoadingState() {
        console.log("[Summary] Showing loading state");
        const sidePanel = document.querySelector(".side-panel-container");
        if (!sidePanel) return;

        sidePanel.classList.add("open");
        document.querySelector(".page-content")?.classList.add("panel-open");

        let logo = sidePanel.querySelector(".side-panel-logo");
        if (!logo) {
            logo = document.createElement("img");
            logo.src = "https://i.imgur.com/aSNdzIx.gif";
            logo.className = "side-panel-logo";
            logo.alt = "Loading...";
            sidePanel.appendChild(logo);
        }
        logo.style.display = 'block';

        const summaryContainer = document.querySelector("#panel-summary .container-content");
        if (summaryContainer) {
            summaryContainer.innerHTML = '';
        }
    },

    hideLoadingState() {
        const logo = document.querySelector(".side-panel-logo");
        if (logo) {
            logo.style.display = 'none';
        }
    },

    updatePanelContent(analysisData) {
        const sidePanel = document.querySelector(".side-panel-container");
        if (!sidePanel) return;

        sidePanel.classList.add("open");
        document.querySelector(".page-content")?.classList.add("panel-open");

        Object.entries(analysisData).forEach(([containerId, data]) => {
            if (!Array.isArray(data) || data.length === 0) return;

            const panelContainer = sidePanel.querySelector(`#panel-${containerId}`);
            const containerContent = panelContainer?.querySelector(".container-content");
            if (!containerContent) return;

            containerContent.innerHTML = this.generateContentHtml(containerId, data);
        });

        // Initialize syntax highlighting if code blocks are present
        if (window.hljs) {
            document.querySelectorAll('pre code').forEach((block) => {
                window.hljs.highlightBlock(block);
            });
        }
    },

    generateContentHtml(type, data) {
        const templates = {
            summary: (item) => `
                <div class="panel-item">
                    <h4>${item.point}</h4>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`,

            todos: (item) => `
                <div class="panel-item">
                    <h4>${item.task}</h4>
                    <p>Priority: ${item.priority}</p>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`,

            references: (item) => `
                <div class="panel-item">
                    <h4><a href="${item.url}" target="_blank" rel="noopener noreferrer">${item.title}</a></h4>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`,

            code: (item) => `
                <div class="panel-item">
                    <h4>${item.language} Code Snippet</h4>
                    <pre><code class="language-${item.language.toLowerCase()}">${item.snippet}</code></pre>
                    ${item.description ? `<p>${item.description}</p>` : ""}
                </div>`,

            embedded: (item) => `
                <div class="panel-item">
                    <h4>${item.type}</h4>
                    <p>${item.content}</p>
                    ${item.description ? `<p>${item.description}</p>` : ""}
                </div>`,

            questions: (item) => `
                <div class="panel-item">
                    <h4>${item.question}</h4>
                    ${item.context ? `<p>${item.context}</p>` : ""}
                </div>`
        };

        return data.map(item => templates[type](item)).join("");
    }
}; 