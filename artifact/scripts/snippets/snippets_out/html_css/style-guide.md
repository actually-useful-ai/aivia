# Chain of Thought Visualization Style Guide

This style guide documents the design system used for the AI reasoning visualization components, providing a reference for consistent implementation across the application.

## Table of Contents

1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Components](#components)
   - [Thought Bubbles](#thought-bubbles)
   - [Chain of Thought](#chain-of-thought)
   - [Streaming Indicators](#streaming-indicators)
4. [Animations](#animations)
5. [Responsive Design](#responsive-design)
6. [Accessibility](#accessibility)
7. [CSS Architecture](#css-architecture)

## Color Palette

The application uses a comprehensive color system with both light and dark themes, controlled via CSS variables.

### Light Theme

| Variable | Value | Usage |
|----------|-------|-------|
| `--primary-bg` | `#ffffff` | Main background |
| `--secondary-bg` | `#f5f5f5` | Secondary/container backgrounds |
| `--primary-text` | `#333333` | Main text color |
| `--secondary-text` | `#666666` | Secondary text, labels |
| `--accent-color` | `#0288d1` | Accent elements, highlights, buttons |
| `--border-color` | `#dde1e4` | Borders, dividers |
| `--thought-bg` | Linear gradient | Thought bubble background |
| `--chain-bg` | `#f9fafb` | Chain of thought container background |
| `--chain-border` | `#e5e7eb` | Borders for chain elements |

### Dark Theme

| Variable | Value | Usage |
|----------|-------|-------|
| `--primary-bg` | `#121212` | Main background |
| `--secondary-bg` | `#1e1e1e` | Secondary/container backgrounds |
| `--primary-text` | `#e2e8f0` | Main text color |
| `--secondary-text` | `#a0aec0` | Secondary text, labels |
| `--accent-color` | `#4299e1` | Accent elements, highlights, buttons |
| `--border-color` | `#2d3748` | Borders, dividers |
| `--thought-bg` | Dark linear gradient | Thought bubble background |
| `--chain-bg` | `#1a1a1a` | Chain of thought container background |
| `--chain-border` | `#2d3748` | Borders for chain elements |

### Rainbow Gradient Colors

Special rainbow gradient effect used for animated borders:

| Variable | Value |
|----------|-------|
| `--rainbow-1` | `#ff0000` (Red) |
| `--rainbow-2` | `#ff8000` (Orange) |
| `--rainbow-3` | `#ffff00` (Yellow) |
| `--rainbow-4` | `#00ff00` (Green) |
| `--rainbow-5` | `#00ffff` (Cyan) |
| `--rainbow-6` | `#0000ff` (Blue) |
| `--rainbow-7` | `#8000ff` (Purple) |
| `--rainbow-8` | `#ff00ff` (Magenta) |

## Typography

The application uses a clean, readable typography system:

- **Primary Font**: System font stack with fallbacks
- **Accent Font**: Playfair Display (400, 700 weights)
- **Monospace**: For code blocks and technical content

### Text Sizes

| Element | Size (Desktop) | Size (Mobile) | Weight |
|---------|----------------|---------------|--------|
| Headers | 1rem - 1.5rem | 0.9rem - 1.3rem | 600-700 |
| Body text | 1rem | 0.9rem | 400 |
| Secondary text | 0.9rem | 0.8rem | 400-500 |
| Labels | 0.8rem | 0.7rem | 600 |

## Components

### Thought Bubbles

Thought bubbles visualize individual steps in the AI's reasoning process.

![Thought Bubble Example](https://via.placeholder.com/450x150?text=Thought+Bubble+Visualization)

#### Visual Characteristics

- **Shape**: Rounded with cloud-like appearance (24px border radius)
- **Background**: Subtle gradient background
- **Shadow**: Soft drop shadow (0 6px 16px) for depth
- **Border**: Thin 1px border
- **Decorative Elements**: Small cloud-like circles positioned outside the bubble

#### States

- **Default**: Semi-transparent (opacity 0.95)
- **Hover**: Increased opacity (1.0), elevated position, deeper shadow

#### Variations

- **Standard Thought**: Default bubble style
- **Solution Transition**: Special highlighted box with "Solution" label and rainbow border animation

### Chain of Thought

Structured visualization of connected reasoning steps.

![Chain of Thought Example](https://via.placeholder.com/450x300?text=Chain+of+Thought+Visualization)

#### Visual Characteristics

- **Container**: Rounded rectangle with subtle background and border
- **Step Connections**: Vertical line connecting sequential steps
- **Step Numbering**: Circular badges with numbers
- **Step Content**: Indented content with clear typography hierarchy

#### States

- **Default**: Flat appearance
- **Hover on Step**: Slight elevation and shadow increase

#### Variations

- **Standard Step**: Regular reasoning step
- **Final Result**: Special highlighted box with accent-colored border and gradient background

### Streaming Indicators

Visual feedback elements for streaming text and loading states.

![Streaming Indicators Example](https://via.placeholder.com/450x100?text=Streaming+Indicators)

#### Visual Characteristics

- **Loading Dots**: Three dots with bounce animation
- **Cursor**: Blinking cursor at text insertion point
- **Thinking Container**: Labeled box for thinking content
- **Progress Line**: Animated gradient line for loading states

#### States

- **Active**: Animated state
- **Complete**: Disappears when no longer needed

## Animations

The interface uses subtle animations to enhance the user experience:

### Thought Bubble Animations

- **Appearance**: Fade-in and upward movement (0.5s duration)
- **Floating**: Gentle vertical floating motion (3s, infinite)
- **Hover**: Slight upward shift and shadow enhancement (0.3s transition)

### Chain of Thought Animations

- **Step Transition**: Bounce animation for direction arrows
- **Hover**: Subtle upward shift (0.3s)

### Streaming Indicators

- **Loading Dots**: Staggered bouncing animation (1.4s)
- **Cursor Blink**: Step-based visibility toggle (1s)
- **Rainbow Border**: Gradient position shift (6s, linear, infinite)
- **Thinking Icon**: Pulsing opacity (2s, infinite)

## Responsive Design

The interface adapts to different screen sizes with the following breakpoints:

### Mobile Breakpoint (max-width: 768px)

- **Thought Bubbles**:
  - Reduced padding (12px vs 16px)
  - Smaller font size (0.9rem vs 1rem)
  - Hidden decorative elements
  - Narrower container (200px vs 300px)

- **Chain of Thought**:
  - Reduced padding (0.75rem vs 1rem)
  - Smaller elements overall
  - Reduced step label size (1.5rem vs 1.75rem)

- **Streaming Indicators**:
  - Smaller loading dots (6px vs 8px)
  - Reduced text size (0.7rem vs 0.8rem)

## Accessibility

The application follows these accessibility principles:

- **Color Contrast**: All text meets WCAG AA standard (4.5:1 minimum contrast ratio)
- **Animation Control**: Animations respect reduced-motion preferences
- **ARIA Attributes**: Proper labeling for dynamic content
- **Focus States**: Visible focus indicators for interactive elements
- **Responsive Text Sizes**: Text scales appropriately across devices

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## CSS Architecture

The CSS is organized into modular files by functionality:

- **variables.css**: Global CSS variables for theming
- **base.css**: Base styles and resets
- **thought-bubbles-styles.css**: Thought bubble visualization
- **chain-of-thought-styles.css**: Chain of thought visualization
- **streaming-indicator-styles.css**: Streaming and loading states
- **responsive.css**: Responsive design adjustments

### Best Practices

1. **Variable-Based Theming**: All colors and key measurements use CSS variables
2. **BEM-Inspired Naming**: Component-based class naming (e.g., `.thought-bubble`, `.chain-step`)
3. **Mobile-First**: Base styles with media queries for larger screens
4. **Performance Considerations**:
   - Transition only transform and opacity properties when possible
   - Use hardware-accelerated animations (transform, opacity)
   - Avoid animating layout properties (width, height, etc.)

---

## Implementation Examples

### Adding a Thought Bubble

```html
<div id="thoughts-container">
  <div class="thought-bubble">
    <p>I need to consider the mathematical properties first...</p>
  </div>
</div>
```

### Creating a Chain of Thought

```html
<div class="chain-of-thought-container">
  <div class="chain-header">
    <div class="chain-title">Reasoning Process</div>
    <div class="chain-controls">
      <button class="chain-control-btn">×</button>
    </div>
  </div>
  <div class="chain-steps">
    <div class="chain-step">
      <div class="step-title">
        <span class="step-label">1</span>
        Initial Analysis
      </div>
      <div class="step-content">
        Let me break down this problem...
      </div>
    </div>
    <!-- Additional steps -->
  </div>
  <div class="chain-result">
    <div class="result-title">Solution</div>
    <div class="result-content">
      Based on my analysis, the answer is...
    </div>
  </div>
</div>
```

### Showing a Loading Indicator

```html
<div class="loading-container">
  <div class="loading-gif">
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
  </div>
</div>
``` 