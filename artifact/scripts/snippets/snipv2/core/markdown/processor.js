/**
 * Markdown Processing
 */

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