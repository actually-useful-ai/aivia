/**
 * Response Format Templates
 */

export const FormatTemplates = {
    /**
     * JSON response format templates
     */
    json: {
        standard: '{"type": "string", "content": "string", "metadata": {}}',
        analysis: '{"summary": [], "details": [], "references": []}',
        evaluation: '{"score": "number", "feedback": "string", "suggestions": []}'
    },

    /**
     * Markdown response format templates
     */
    markdown: {
        article: '# Title\n## Summary\n[content]\n## Details\n[content]\n## References\n[content]',
        review: '## Strengths\n[content]\n## Weaknesses\n[content]\n## Suggestions\n[content]',
        analysis: '## Key Points\n[content]\n## Evidence\n[content]\n## Conclusion\n[content]'
    },

    /**
     * Structured text response format templates
     */
    structured: {
        report: 'TITLE:\n[content]\nFINDINGS:\n[content]\nRECOMMENDATIONS:\n[content]',
        feedback: 'POSITIVE:\n[content]\nAREAS FOR IMPROVEMENT:\n[content]\nNEXT STEPS:\n[content]',
        summary: 'OVERVIEW:\n[content]\nDETAILS:\n[content]\nCONCLUSION:\n[content]'
    }
}; 