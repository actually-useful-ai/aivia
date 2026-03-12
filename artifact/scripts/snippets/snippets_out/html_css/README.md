# AI Chain of Thought Visualization CSS Snippets

This collection of CSS snippets provides modular, reusable components for visualizing AI reasoning processes and thought states. These components enhance the user experience by making AI thinking more transparent.

## Contents

1. **theme-variables.css** - Core theme variables used across all components
2. **thought-bubble.css** - Cloud-like thought bubbles for AI intermediary thoughts
3. **solution-box.css** - Highlighted solution boxes with rainbow gradient borders
4. **loading-indicators.css** - Loading animations and streaming indicators
5. **chain-of-thought.css** - Connected reasoning step visualization

## Usage

### Quick Start

1. Copy the `theme-variables.css` file into your project
2. Import or copy individual component styles as needed
3. Add the required HTML structure for each component
4. Customize as needed for your application

### Theme Support

All components support light and dark themes out of the box using CSS variables. To toggle between themes:

```js
// Switch to dark theme
document.documentElement.setAttribute('data-theme', 'dark');

// Switch to light theme
document.documentElement.setAttribute('data-theme', 'light');

// Or toggle based on user preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
```

## Component Examples

### Thought Bubbles

Animated cloud-like bubbles for visualizing AI's internal thoughts:

```html
<div id="thoughts-container">
  <div class="thought-bubble">
    <p>I need to consider the mathematical properties first...</p>
  </div>
  <div class="thought-bubble">
    <p>Let me try a different approach...</p>
  </div>
</div>
```

### Solution Box

Highlighted box for final answers with rainbow gradient border:

```html
<div class="thought-to-solution">
  <p>Based on my analysis, the answer is 42.</p>
</div>

<!-- With custom label -->
<div class="thought-to-solution" data-label="Final Answer">
  <p>The solution is to implement a binary search algorithm.</p>
</div>
```

### Loading Indicators

Various loading animations for streaming responses:

```html
<!-- Loading dots -->
<div class="loading-container">
  <div class="loading-gif">
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
  </div>
</div>

<!-- Streaming indicator -->
<div class="streaming-indicator">
  <div class="streaming-spinner"></div>
  <span>Generating response...</span>
</div>
```

### Chain of Thought

Connected reasoning steps with progressive flow:

```html
<div class="chain-of-thought-container">
  <div class="chain-header">
    <div class="chain-title">Problem Solving Approach</div>
  </div>
  <div class="chain-steps">
    <div class="chain-step">
      <div class="step-title">
        <span class="step-label">1</span>
        Understanding the Problem
      </div>
      <div class="step-content">
        First, I need to analyze what's being asked...
      </div>
    </div>
    <!-- More steps -->
  </div>
  <div class="chain-result">
    <div class="result-title">Solution</div>
    <div class="result-content">
      The final answer is...
    </div>
  </div>
</div>
```

## Accessibility Features

- All components respect reduced motion preferences
- Color contrast ratios meet WCAG AA standards
- Screen reader compatible with proper ARIA attributes
- Keyboard navigable interactive elements

## Customization

Each component can be customized by modifying the CSS variables in `theme-variables.css`. For example:

```css
:root {
  --accent-color: #8e44ad; /* Change accent color to purple */
  --thought-bg: linear-gradient(145deg, #f3e5f5, #e1bee7); /* Change thought bubble color */
}
```

## Browser Support

These components are compatible with all modern browsers (Chrome, Firefox, Safari, Edge). Internet Explorer is not supported due to CSS variable usage.

## License

MIT License - Feel free to use, modify, and distribute as needed.

---

These CSS snippets were extracted and optimized from an actual production application that visualizes AI reasoning processes for users. 