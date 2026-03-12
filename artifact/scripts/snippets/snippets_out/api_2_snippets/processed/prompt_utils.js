/**
 * Prompt Utilities and Templates
 * Consolidated from multiple files
 */

// Alt Text Generation Prompts
export const AltTextPrompts = {
    // Base prompt for standard alt text generation
    base: `You're an Alt Text Specialist, dedicated to creating precise and accessible alt text for digital images, especially memes. Your primary goal is to ensure visually impaired individuals can engage with imagery by providing concise, accurate, and ethically-minded descriptions.

        Skill 1: Create Alt Text

        - **Depict essential visuals and visible text accurately.**
        - **Avoid adding social-emotional context or narrative interpretations unless specifically requested.**
        - **Refrain from speculating on artists' intentions.**
        - **Avoid prepending with "Alt text:" for direct usability.**
        - **Maintain clarity and consistency for all descriptions, including direct image links.**
        - **Character limit:** All descriptions must be under 1000 characters.`,

    // Specialized interpretation prompts
    interpretations: {
        socialEmotional: `Using MAXIMUM detail and token count, reply with a social and emotional interpretation based on visible expressions, body language, or context within the image. What's going on here socially? What do the characters feel emotionally?`,

        humor: `Using MAXIMUM detail and token count, reply with a description of the image's humor, interpret comedic elements, including any visible punchlines or jokes in the image. What's the joke? Why is it funny?`,

        artistic: `Using MAXIMUM detail and token count, reply with an artistic interpretation, noting the style, symbols, or unique artistic qualities present in the image. What kind of art is it? Any specific period or genre? What's the aesthetic?`,

        cultural: `Using MAXIMUM detail and token count, reply with a description capturing cultural elements, symbols, attire, or settings that may carry specific significance to viewers. Why does it matter culturally? Is it significant? What does it say about the moment and its context?`,

        character: `Using MAXIMUM detail and token count, reply providing insights into the intent, expressions, or actions of any characters or subjects within the image. What are they doing, and why? What's the overall point that the image conveys?`
    },

    // Modification commands
    commands: {
        shorter: `The above alt text is too long for social media. Please regenerate it at half of the normal length, still capturing the critical details.`,
        longer: `The above alt text was too short and not detailed enough. Regenerate the response and reply again at double the normal length and detail.`,
        retry: `The alt text above wasn't accurate. Alter your assumptions and approach and reply again in a different way.`,
        enhance: `The alt text above isn't accurate or was lacking. Use Google Lens search to learn more about this image and its context, then reply again with alt text as usual.`
    }
};

// Academic Writing Prompts
export const AcademicPrompts = {
    // Citation analysis prompts
    citations: {
        analyze: `Analyze the following citation and provide a structured breakdown of its components, including author contributions, methodology, key findings, and potential impact.`,
        
        synthesize: `Compare and contrast the following citations, identifying common themes, contradictions, and potential gaps in the research. Consider methodology differences and their implications.`,
        
        evaluate: `Evaluate the strength of this citation's evidence and argumentation. Consider research design, sample size, methodology, and potential biases.`
    },

    // Literature review prompts
    literature: {
        summarize: `Provide a comprehensive summary of this literature, focusing on key themes, methodological approaches, and significant findings. Identify any patterns or trends in the research.`,
        
        critique: `Critically evaluate this literature, examining strengths, limitations, and potential biases. Consider the validity of conclusions and generalizability of findings.`,
        
        integrate: `Integrate findings from multiple sources to create a cohesive narrative about the current state of knowledge in this area. Identify gaps and future research directions.`
    },

    // Research writing prompts
    research: {
        abstract: `Generate a structured abstract for this research, including background, methods, results, and conclusions. Follow standard academic conventions and maintain clarity.`,
        
        methods: `Describe the research methodology in detail, including study design, data collection procedures, analysis methods, and any relevant statistical approaches.`,
        
        discussion: `Develop a comprehensive discussion of the research findings, considering theoretical implications, practical applications, limitations, and future directions.`
    }
};

// Prompt Management Utilities
export const PromptManager = {
    // Combine multiple prompts with proper formatting
    combinePrompts(prompts, separator = "\n\n") {
        return prompts.filter(Boolean).join(separator);
    },

    // Add specific constraints to a prompt
    addConstraints(prompt, constraints) {
        const constraintText = Object.entries(constraints)
            .map(([key, value]) => `${key}: ${value}`)
            .join("\n");
        return `${prompt}\n\nConstraints:\n${constraintText}`;
    },

    // Create a structured prompt with multiple sections
    createStructuredPrompt(sections) {
        return Object.entries(sections)
            .map(([heading, content]) => `${heading}:\n${content}`)
            .join("\n\n");
    },

    // Add examples to a prompt
    addExamples(prompt, examples) {
        const exampleText = examples
            .map(ex => `Input: ${ex.input}\nOutput: ${ex.output}`)
            .join("\n\n");
        return `${prompt}\n\nExamples:\n${exampleText}`;
    },

    // Create a prompt with specific formatting requirements
    withFormatting(prompt, format) {
        return `${prompt}\n\nRequired Format:\n${format}`;
    }
};

// Response Format Templates
export const FormatTemplates = {
    // JSON response format
    json: {
        standard: '{"type": "string", "content": "string", "metadata": {}}',
        analysis: '{"summary": [], "details": [], "references": []}',
        evaluation: '{"score": "number", "feedback": "string", "suggestions": []}'
    },

    // Markdown response format
    markdown: {
        article: '# Title\n## Summary\n[content]\n## Details\n[content]\n## References\n[content]',
        review: '## Strengths\n[content]\n## Weaknesses\n[content]\n## Suggestions\n[content]',
        analysis: '## Key Points\n[content]\n## Evidence\n[content]\n## Conclusion\n[content]'
    },

    // Structured text response format
    structured: {
        report: 'TITLE:\n[content]\nFINDINGS:\n[content]\nRECOMMENDATIONS:\n[content]',
        feedback: 'POSITIVE:\n[content]\nAREAS FOR IMPROVEMENT:\n[content]\nNEXT STEPS:\n[content]',
        summary: 'OVERVIEW:\n[content]\nDETAILS:\n[content]\nCONCLUSION:\n[content]'
    }
}; 