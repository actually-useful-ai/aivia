/**
 * Link Embedding
 */

export const LinkEmbedder = {
    // Regular expressions for different link types
    patterns: {
        youtube: /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/,
        pdf: /^(https?:\/\/[^\s]+\.pdf)$/i,
        doi: /^(?:https?:\/\/(?:dx\.)?doi\.org\/|doi:)(10\.\d{4,}\/\S+)$/i,
        pubmed: /^https?:\/\/(?:www\.)?ncbi\.nlm\.nih\.gov\/pubmed\/(\d+)$/i
    },

    // Embed YouTube videos
    embedYouTube(videoId) {
        console.log("[Links] Embedding YouTube:", videoId);
        return `
            <div class="video-container">
                <iframe src="https://www.youtube.com/embed/${videoId}" 
                        frameborder="0" 
                        allowfullscreen
                        title="YouTube video player">
                </iframe>
            </div>`;
    },

    // Handle PDF embedding
    async validatePDFUrl(url) {
        try {
            const response = await fetch(url, { method: 'HEAD' });
            const contentType = response.headers.get('content-type');
            return response.ok && contentType && contentType.includes('pdf');
        } catch (error) {
            console.error('[PDF] Validation failed:', error);
            return false;
        }
    },

    embedPDF(url) {
        return `
            <div class="pdf-embed-container">
                <iframe class="pdf-viewer" 
                        src="${url}" 
                        frameborder="0"
                        title="PDF document viewer">
                </iframe>
                <div class="pdf-fallback">
                    <p>Unable to display PDF. <a href="${url}" target="_blank" rel="noopener noreferrer">Open PDF</a></p>
                </div>
            </div>`;
    },

    // Handle citations
    async fetchCitation(doi) {
        try {
            const response = await fetch(`https://api.crossref.org/works/${doi}`);
            const data = await response.json();
            return data.message;
        } catch (error) {
            console.error('[Citation] Fetch failed:', error);
            return null;
        }
    },

    embedCitation(citation) {
        if (!citation) return '';
        return `
            <div class="citation-card">
                <h3>${citation.title[0]}</h3>
                <div class="citation-authors">${citation.author.map(a => `${a.given} ${a.family}`).join(', ')}</div>
                <div class="citation-journal">${citation.publisher} (${citation['published-print']?.['date-parts']?.[0]?.[0] || 'n.d.'})</div>
                <div class="citation-metrics">
                    ${citation['is-referenced-by-count'] ? `<span>Cited by: ${citation['is-referenced-by-count']}</span>` : ''}
                </div>
            </div>`;
    },

    // Process links in markdown content
    async processLinks(content, md) {
        const tokens = md.parse(content, {});
        
        for (let i = 0; i < tokens.length; i++) {
            if (tokens[i].type !== "inline") continue;

            const children = tokens[i].children;
            for (let j = 0; j < children.length; j++) {
                const token = children[j];

                if (token.type === "link_open") {
                    const hrefIndex = token.attrIndex("href");
                    if (hrefIndex >= 0) {
                        const href = token.attrs[hrefIndex][1];
                        await this.handleLink(href, token, children, j, md);
                    }
                }
            }
        }

        return md.renderer.render(tokens, md.options);
    },

    // Handle different types of links
    async handleLink(href, token, children, index, md) {
        let match;

        // YouTube videos
        if ((match = this.patterns.youtube.exec(href))) {
            const videoId = match[1];
            this.replaceTokens(children, index, this.embedYouTube(videoId));
        }
        // PDFs
        else if (this.patterns.pdf.test(href)) {
            const isValid = await this.validatePDFUrl(href);
            const content = isValid 
                ? this.embedPDF(href)
                : `<div class="pdf-embed-container error">
                    <p>PDF not available. <a href="${href}" target="_blank" rel="noopener noreferrer">Try opening directly</a></p>
                   </div>`;
            this.replaceTokens(children, index, content);
        }
        // DOIs and PubMed
        else if (this.patterns.doi.test(href) || this.patterns.pubmed.test(href)) {
            const citation = await this.fetchCitation(href);
            const content = citation
                ? this.embedCitation(citation)
                : `<div class="citation-card error">
                    <p>Citation not available. <a href="${href}" target="_blank" rel="noopener noreferrer">Try opening directly</a></p>
                   </div>`;
            this.replaceTokens(children, index, content);
        }
    },

    // Replace tokens with embedded content
    replaceTokens(children, startIndex, content) {
        let endIndex = startIndex + 1;
        while (endIndex < children.length && children[endIndex].type !== "link_close") {
            endIndex++;
        }
        
        const htmlToken = new children[startIndex].constructor("html_block", "", 0);
        htmlToken.content = content;
        
        children.splice(startIndex, endIndex - startIndex + 1, htmlToken);
    }
}; 