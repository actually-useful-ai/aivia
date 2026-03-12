/**
 * Markdown Processing and Link Embedding Utilities
 */

// Markdown Configuration and Initialization
export const MarkdownProcessor = {
    initializeMarkdown() {
        console.log("[Markdown] Initializing parser");
        const md = window
            .markdownit({
                html: true,
                breaks: true,
                linkify: true,
                typographer: true,
                highlight: (str, lang) => {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            console.log("[Markdown] Highlighting:", lang);
                            return `<pre class="hljs"><code>${
                                hljs.highlight(str, { language: lang, ignoreIllegals: true })
                                    .value
                            }</code></pre>`;
                        } catch (error) {
                            console.error("[Markdown] Highlight error:", error);
                        }
                    }
                    console.log("[Markdown] Using plaintext");
                    const escapedStr = md.utils.escapeHtml(str);
                    return `<pre class="hljs"><code>${escapedStr}</code></pre>`;
                },
            })
            .use(window.markdownitTaskLists)
            .use(window.markdownitFootnote)
            .use(window.markdownitSub)
            .use(window.markdownitSup)
            .use(window.markdownitDeflist)
            .use(window.markdownitAbbr)
            .use(window.markdownitMark)
            .use(window.markdownitMultimdTable, {
                multiline: true,
                rowspan: true,
                headerless: true,
                multibody: true
            })
            .use(window.markdownitKatex, {
                throwOnError: false,
                displayMode: true,
                output: 'html',
                strict: false
            })
            .use(window.markdownitCitations, {
                strict: false,
                format: 'apa'
            });

        // Add inline math support
        md.inline.ruler.before('escape', 'math_inline', (state, silent) => {
            const delimiter = '$';
            if (state.src[state.pos] !== delimiter) return false;
            
            const start = state.pos;
            const max = state.posMax;
            
            state.pos++;
            while (state.pos < max && state.src[state.pos] !== delimiter) {
                state.pos++;
            }
            
            if (state.pos === max || state.src[state.pos] !== delimiter) {
                state.pos = start;
                return false;
            }
            
            const content = state.src.slice(start + 1, state.pos);
            if (!silent) {
                const token = state.push('math_inline', '', 0);
                token.content = content;
                token.markup = delimiter;
            }
            
            state.pos++;
            return true;
        });

        // Add accessibility enhancements
        md.renderer.rules.math_inline = (tokens, idx) => {
            const content = tokens[idx].content;
            return `<span class="math-inline" role="math" aria-label="${content}">${content}</span>`;
        };

        md.renderer.rules.math_block = (tokens, idx) => {
            const content = tokens[idx].content;
            return `<div class="math-block" role="math" aria-label="Mathematical expression: ${content}">${content}</div>`;
        };

        md.renderer.rules.footnote_ref = (tokens, idx, options, env, slf) => {
            const id = slf.rules.footnote_anchor_name(tokens, idx, options, env, slf);
            const caption = slf.rules.footnote_caption(tokens, idx, options, env, slf);
            return `<sup class="footnote-ref" role="doc-noteref">
                     <a href="#fn${id}" id="fnref${id}" aria-label="Footnote ${caption}">${caption}</a>
                   </sup>`;
        };

        md.renderer.rules.footnote_block_open = () => {
            return `<section class="footnotes" role="doc-endnotes">
                    <h2 class="sr-only">Footnotes</h2>
                    <ol role="list">`;
        };

        console.log("[Markdown] Parser initialized with academic features");
        return md;
    },

    // Academic writing enhancements
    academicFeatures: {
        // Citation styles (APA, MLA, Chicago, IEEE, Harvard)
        citationStyles: {
            apa: {
                formatInText: (author, year) => `(${author}, ${year})`,
                formatReference: (ref) => {
                    const authors = ref.authors.join(', ');
                    return `${authors} (${ref.year}). ${ref.title}. ${ref.journal}, ${ref.volume}(${ref.issue}), ${ref.pages}.`;
                }
            },
            mla: {
                formatInText: (author, page) => `(${author} ${page})`,
                formatReference: (ref) => {
                    const authors = ref.authors.join(', ');
                    return `${authors}. "${ref.title}." ${ref.journal}, vol. ${ref.volume}, no. ${ref.issue}, ${ref.year}, pp. ${ref.pages}.`;
                }
            },
            chicago: {
                formatInText: (author, year) => `(${author} ${year})`,
                formatReference: (ref) => {
                    const authors = ref.authors.map(a => `${a.family}, ${a.given}`).join(', ');
                    return `${authors}. "${ref.title}." ${ref.journal} ${ref.volume}, no. ${ref.issue} (${ref.year}): ${ref.pages}.`;
                }
            },
            ieee: {
                formatInText: (index) => `[${index}]`,
                formatReference: (ref, index) => {
                    const authors = ref.authors.map(a => `${a.initials}. ${a.family}`).join(', ');
                    return `[${index}] ${authors}, "${ref.title}," ${ref.journal}, vol. ${ref.volume}, no. ${ref.issue}, pp. ${ref.pages}, ${ref.year}.`;
                }
            },
            harvard: {
                formatInText: (author, year) => `(${author}, ${year})`,
                formatReference: (ref) => {
                    const authors = ref.authors.map(a => `${a.family}, ${a.given[0]}.`).join(', ');
                    return `${authors} ${ref.year}. ${ref.title}. ${ref.journal}, ${ref.volume}(${ref.issue}), pp.${ref.pages}.`;
                }
            }
        },

        // Bibliography management
        bibliographyManager: {
            references: [],
            citationCount: {},

            addReference(ref) {
                const id = this.generateCitationId(ref);
                if (!this.citationCount[id]) {
                    this.references.push({ ...ref, id });
                    this.citationCount[id] = 1;
                } else {
                    this.citationCount[id]++;
                }
                return id;
            },

            generateCitationId(ref) {
                return `${ref.authors[0].family.toLowerCase()}${ref.year}`;
            },

            formatBibliography(style = 'apa') {
                const formatter = this.citationStyles[style].formatReference;
                return this.references
                    .sort((a, b) => a.authors[0].family.localeCompare(b.authors[0].family))
                    .map((ref, index) => formatter(ref, index + 1))
                    .join('\n\n');
            }
        },

        // Figure and table numbering
        contentNumbering: {
            figures: 1,
            tables: 1,
            equations: 1,
            
            getNextNumber(type) {
                return this[type]++;
            },
            
            formatFigure(caption, imageUrl = '') {
                const num = this.getNextNumber('figures');
                return `<figure role="figure" aria-labelledby="fig-${num}">
                          ${imageUrl ? `<img src="${imageUrl}" alt="${caption}">` : ''}
                          <figcaption id="fig-${num}">Figure ${num}: ${caption}</figcaption>
                        </figure>`;
            },
            
            formatTable(caption, content) {
                const num = this.getNextNumber('tables');
                return `<div role="table" aria-labelledby="table-${num}">
                          <div id="table-${num}" class="table-caption">Table ${num}: ${caption}</div>
                          ${content}
                        </div>`;
            },

            formatEquation(equation, label = '') {
                const num = this.getNextNumber('equations');
                return `<div class="equation-container" role="math" aria-label="Equation ${num}${label ? ': ' + label : ''}">
                          <div class="equation" id="eq-${num}">${equation}</div>
                          <div class="equation-number">(${num})</div>
                        </div>`;
            }
        },

        // Academic document sections
        documentSections: {
            abstract: (content) => `
                <section class="abstract" role="doc-abstract" aria-label="Abstract">
                    <h2>Abstract</h2>
                    <div class="abstract-content">${content}</div>
                </section>`,

            keywords: (keywords) => `
                <section class="keywords" role="doc-keywords" aria-label="Keywords">
                    <h3>Keywords</h3>
                    <div class="keywords-list">${keywords.join(', ')}</div>
                </section>`,

            acknowledgments: (content) => `
                <section class="acknowledgments" role="doc-acknowledgments" aria-label="Acknowledgments">
                    <h2>Acknowledgments</h2>
                    <div class="acknowledgments-content">${content}</div>
                </section>`
        }
    }
};

// Link Embedding
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