/**
 * chain-of-thought-processor.js
 * Processes LLM chain of thought output for visualization
 * 
 * This snippet shows how to parse and visualize LLM outputs that include thought processes
 * marked with special tags, such as those from Openthinker, DeepSeek, or similar models.
 */

/**
 * Process message content, handling thought formatting
 * @param {string} content - The message content
 * @param {Object} md - The markdown-it instance
 * @returns {string} - The processed HTML content
 */
export function processMessageContent(content, md) {
    // Remove end tags if present
    content = content.replace(/<\|end_of_solution\|>$/, '');
    content = content.replace(/<\|\/answer\|>$/, '');
    
    if (!content) return '';
    
    // Check for various chain of thought formats
    if (content.includes('<|begin_of_thought|>') || content.includes('<|thinking|>') || content.includes('<|answer|>')) {
        console.log('Detected chain of thought format:', content);
        
        // Special case for DeepSeek answer without thinking tags
        if (content.includes('<|answer|>') && !content.includes('<|thinking|>') && !content.includes('<|begin_of_thought|>')) {
            return processAnswerOnlyContent(content, md);
        }
        
        // Handle both Openthinker and Deepseek tag formats
        let thoughtStartTag = content.includes('<|begin_of_thought|>') ? '<|begin_of_thought|>' : '<|thinking|>';
        let thoughtEndTag = content.includes('<|end_of_thought|>') ? '<|end_of_thought|>' : '<|/thinking|>';
        let solutionStartTag = content.includes('<|begin_of_solution|>') ? '<|begin_of_solution|>' : '<|answer|>';
        let solutionEndTag = content.includes('<|end_of_solution|>') ? '<|end_of_solution|>' : '<|/answer|>';
        
        return processThoughtsSolution(content, thoughtStartTag, thoughtEndTag, solutionStartTag, solutionEndTag, md);
    }
    
    // Fall back to standard markdown rendering if no special tags
    return md.render(content);
}

/**
 * Process answer-only content (no thought sections)
 * @param {string} content - The message content
 * @param {Object} md - The markdown-it instance
 * @returns {string} - The processed HTML content
 */
function processAnswerOnlyContent(content, md) {
    const parts = content.split('<|answer|>');
    const beforeAnswer = parts[0] || '';
    let answerContent = parts[1] || '';
    
    // Remove answer end tag if present
    answerContent = answerContent.replace(/<\|\/answer\|>$/, '');
    
    // Create the solution container
    const solutionHtml = `<div class="thought-to-solution">${md.render(answerContent.trim())}</div>`;
    
    // Combine with any content before the answer tag
    let finalContent = '';
    if (beforeAnswer.trim()) {
        finalContent += md.render(beforeAnswer.trim());
    }
    finalContent += solutionHtml;
    
    return finalContent;
}

/**
 * Process thoughts and solution content
 * @param {string} content - The message content
 * @param {string} thoughtStartTag - The tag that starts the thought section
 * @param {string} thoughtEndTag - The tag that ends the thought section
 * @param {string} solutionStartTag - The tag that starts the solution section
 * @param {string} solutionEndTag - The tag that ends the solution section
 * @param {Object} md - The markdown-it instance
 * @returns {string} - The processed HTML content
 */
function processThoughtsSolution(content, thoughtStartTag, thoughtEndTag, solutionStartTag, solutionEndTag, md) {
    let parts = content.split(thoughtStartTag);
    let beforeThought = parts[0];
    let afterThought = parts[1] || '';
    
    // If we have an ending thought tag
    if (afterThought.includes(thoughtEndTag)) {
        let [thoughtContent, remainingContent] = afterThought.split(thoughtEndTag);
        
        // Process thoughts - group list items together
        let thoughts = processThoughtContent(thoughtContent, md);
        
        // Check if we have a solution marker
        if (remainingContent) {
            let solutionContent = remainingContent;
            
            // Handle solution start tag if present
            if (solutionContent.includes(solutionStartTag)) {
                const solutionParts = solutionContent.split(solutionStartTag);
                const beforeSolution = solutionParts[0] || '';
                solutionContent = solutionParts[1] || '';
                
                // Add any content between end_of_thought and begin_of_solution
                if (beforeSolution.trim()) {
                    thoughts += md.render(beforeSolution.trim());
                }
            }
            
            // Remove solution end tag if present
            solutionContent = solutionContent.replace(new RegExp(solutionEndTag + '$'), '');
            
            // Create the solution container with a clear indicator
            const solutionHtml = `<div class="thought-to-solution">${md.render(solutionContent.trim())}</div>`;
            
            // Combine with any remaining content
            let finalContent = '';
            if (beforeThought.trim()) {
                finalContent += md.render(beforeThought.trim());
            }
            finalContent += thoughts;
            finalContent += solutionHtml;
            
            return finalContent;
        } else {
            // No solution yet, just thoughts
            let finalContent = '';
            if (beforeThought.trim()) {
                finalContent += md.render(beforeThought.trim());
            }
            finalContent += thoughts;
            
            return finalContent;
        }
    } else {
        // No thought end tag yet, possibly a partial message during streaming
        return md.render(content);
    }
}

/**
 * Process thought content, handling list items specially
 * @param {string} thoughtContent - The thought content
 * @param {Object} md - The markdown-it instance
 * @returns {string} - The processed HTML content for thoughts
 */
function processThoughtContent(thoughtContent, md) {
    let lines = thoughtContent.split('\n').filter(line => line.trim());
    let thoughts = '';
    let currentListType = null;
    let listItems = [];
    
    // Process each line
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const isBulletList = /^\s*[-*]/.test(line);
        const isNumberedList = /^\s*\d+\./.test(line);
        const isList = isBulletList || isNumberedList;
        
        // Handle list items
        if (isList) {
            // Determine list type
            const newListType = isBulletList ? 'ul' : 'ol';
            
            // If this is a new list or different type of list
            if (currentListType !== newListType) {
                // Close previous list if exists
                if (listItems.length > 0) {
                    const listHtml = `<${currentListType}>${listItems.join('')}</${currentListType}>`;
                    thoughts += `<div class="thought-bubble">${listHtml}</div>`;
                    listItems = [];
                }
                
                // Start new list
                currentListType = newListType;
            }
            
            // Process list item content
            let itemContent;
            if (isBulletList) {
                itemContent = line.trim().substring(1);
            } else {
                itemContent = line.trim().substring(line.indexOf('.')+1);
            }
            
            // Add to list items
            listItems.push(`<li>${md.render(itemContent.trim())}</li>`);
            
            // If this is the last line or next line is not a list, close the list
            if (i === lines.length - 1 || 
                !/^\s*[-*]/.test(lines[i+1]) && !/^\s*\d+\./.test(lines[i+1])) {
                const listHtml = `<${currentListType}>${listItems.join('')}</${currentListType}>`;
                thoughts += `<div class="thought-bubble">${listHtml}</div>`;
                listItems = [];
                currentListType = null;
            }
        } else {
            // Close any open list
            if (listItems.length > 0) {
                const listHtml = `<${currentListType}>${listItems.join('')}</${currentListType}>`;
                thoughts += `<div class="thought-bubble">${listHtml}</div>`;
                listItems = [];
                currentListType = null;
            }
            
            // Regular thought bubble
            thoughts += `<div class="thought-bubble">${md.render(line.trim())}</div>`;
        }
    }
    
    return thoughts;
}

/**
 * Example CSS for chain of thought visualization
 * Add this to your CSS file
 */
/*
.thought-to-solution {
    background-color: #e8f5e9;
    border-left: 4px solid #66bb6a;
    padding: 12px 15px;
    margin: 15px 0;
    position: relative;
    border-radius: 4px;
}

.thought-to-solution::before {
    content: "Answer";
    position: absolute;
    top: -10px;
    left: 10px;
    background-color: #4caf50;
    color: white;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
}
*/ 