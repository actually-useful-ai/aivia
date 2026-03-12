/**
 * Summary UI Management
 */

export const SummaryUIManager = {
    /**
     * Shows the loading state
     */
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

    /**
     * Hides the loading state
     */
    hideLoadingState() {
        const logo = document.querySelector(".side-panel-logo");
        if (logo) {
            logo.style.display = 'none';
        }
    },

    /**
     * Updates the panel content with analysis data
     * @param {Object} analysisData - The analysis data
     */
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

    /**
     * Generates HTML content for different types of data
     * @param {string} type - The type of content
     * @param {Array} data - The content data
     * @returns {string} The generated HTML
     */
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