# LLM Eval Hub - Usage Guide

This guide explains how to use the generated CSS and JavaScript files in your HTML.

## Basic HTML Template

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LLM Eval Hub</title>

  <!-- CSS Files (in order) -->
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="css/responsive.css">
  <link rel="stylesheet" href="css/animations.css">
</head>
<body>
  <!-- Your HTML content here -->

  <!-- JavaScript Files (at end of body) -->
  <script src="js/theme-toggle.js"></script>
  <script src="js/main.js"></script>
  <script src="js/search.js"></script>
</body>
</html>
```

## CSS File Inclusion

### style.css (Required)
The main stylesheet containing:
- CSS custom properties (colors, spacing, typography)
- Base element styles
- Layout components (container, sections, grids)
- Navigation and hero section
- Cards, tables, buttons, badges
- Footer and utility classes

Include first to establish base styles.

### responsive.css (Recommended)
Responsive design breakpoints and adjustments:
- Mobile hamburger menu visibility
- Grid layout changes at different screen sizes
- Typography scaling
- Touch-friendly target sizing
- Print styles

Include after style.css for responsive overrides.

### animations.css (Optional)
Animation definitions and keyframes:
- Scroll-triggered animations
- Hover effects
- Loading animations
- Transition utilities

Include after responsive.css. Can be omitted if animations not needed.

## JavaScript File Inclusion

### theme-toggle.js (Recommended)
Provides dark/light mode toggle functionality:
- Detects system preference (prefers-color-scheme)
- Saves user preference to localStorage
- Provides smooth theme transitions
- Updates toggle button icons

Include first for early theme detection.

### main.js (Recommended)
Core interactive features:
- Scroll animations with Intersection Observer
- Mobile hamburger menu
- Smooth anchor navigation
- Active nav link highlighting
- Back-to-top button
- Glossary expansion

Essential for interactivity. Include after theme-toggle.js.

### search.js (Optional)
Filtering and search functionality:
- Benchmark category filters
- Text-based search
- Advanced multi-criteria search
- Card sorting
- Screen reader announcements

Include only if using filtering/search features.

## Using CSS Classes

### Layout

```html
<div class="container">
  <section class="section">
    <!-- Content -->
  </section>
</div>
```

### Grids

```html
<!-- 3 equal columns -->
<div class="grid-3">
  <div class="card"><!-- Card 1 --></div>
  <div class="card"><!-- Card 2 --></div>
  <div class="card"><!-- Card 3 --></div>
</div>

<!-- Responsive: 4 columns on large, 2 on tablet, 1 on mobile -->
<div class="grid-4">
  <!-- Cards -->
</div>
```

### Cards

```html
<div class="card fade-in">
  <div class="card-header">
    <div class="card-icon">📊</div>
    <div>
      <h4 class="card-title">Card Title</h4>
      <p class="card-description">Description text</p>
    </div>
  </div>
  <p>Card content here</p>
  <div class="card-footer">
    <span class="badge badge-category">Category</span>
    <a href="#" class="text-accent">Learn more</a>
  </div>
</div>
```

### Buttons

```html
<!-- Primary button -->
<button class="btn btn-primary">Action</button>

<!-- Secondary button -->
<button class="btn btn-secondary">Alternative</button>

<!-- Different sizes -->
<button class="btn btn-primary btn-small">Small</button>
<button class="btn btn-primary btn-large">Large</button>
```

### Badges

```html
<span class="badge badge-category">Framework</span>
<span class="badge badge-difficulty-easy">Easy</span>
<span class="badge badge-difficulty-medium">Medium</span>
<span class="badge badge-difficulty-hard">Hard</span>
```

### Navigation

```html
<nav>
  <div class="container">
    <div class="logo">LLM Eval Hub</div>

    <div class="hamburger" id="hamburger">
      <span></span>
      <span></span>
      <span></span>
    </div>

    <ul class="nav-links">
      <li><a href="#benchmarks">Benchmarks</a></li>
      <li><a href="#frameworks">Frameworks</a></li>
      <li><a href="#glossary">Glossary</a></li>
      <button class="theme-toggle" aria-label="Toggle theme"></button>
    </ul>
  </div>
</nav>
```

### Hero Section

```html
<section class="hero">
  <div class="container">
    <div class="hero-content">
      <h1>Large Language Model Evaluation</h1>
      <p>Comprehensive frameworks and benchmarks for LLM assessment</p>
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-number">50+</div>
          <div class="stat-label">Benchmarks</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">20+</div>
          <div class="stat-label">Frameworks</div>
        </div>
      </div>
    </div>
  </div>
</section>
```

### Expandable Glossary

```html
<div class="glossary-item">
  <div class="glossary-term">
    <span>Term Definition</span>
    <span class="glossary-toggle">▼</span>
  </div>
  <div class="glossary-definition">
    <p>Detailed definition and explanation of the term goes here.</p>
  </div>
</div>
```

### Timeline

```html
<div class="timeline">
  <div class="timeline-item">
    <div class="timeline-date">2024 Q1</div>
    <div class="timeline-title">Milestone</div>
    <div class="timeline-description">Description</div>
  </div>
  <!-- More timeline items -->
</div>
```

## Using Animation Classes

Add animation classes for scroll-triggered effects:

```html
<!-- Fade in on scroll -->
<div class="fade-in">Content</div>

<!-- Slide up on scroll -->
<div class="slide-up">Content</div>

<!-- Slide from left on scroll -->
<div class="slide-left">Content</div>

<!-- Slide from right on scroll -->
<div class="slide-right">Content</div>

<!-- Scale in on scroll -->
<div class="scale-in">Content</div>

<!-- Staggered animations -->
<div class="fade-in stagger-1">First</div>
<div class="fade-in stagger-2">Second</div>
<div class="fade-in stagger-3">Third</div>
```

## Using JavaScript APIs

### Theme Control

```javascript
// Get current theme
const theme = window.ThemeToggle.getCurrentTheme();
// Returns: 'light' or 'dark'

// Set theme
window.ThemeToggle.setTheme('light');

// Toggle theme
window.ThemeToggle.toggleTheme();

// From anywhere
window.setAppTheme('dark');
const currentTheme = window.getAppTheme();
```

### Search and Filter

```javascript
// Filter cards by category
const cards = document.querySelectorAll('[data-category]');
window.BenchmarkSearch.filterCards(cards, 'data-category', 'framework');

// Advanced search
window.BenchmarkSearch.advancedSearch(cards, {
  category: 'framework',
  difficulty: 'hard'
});

// Reset filters
window.BenchmarkSearch.resetFilters();

// Sort cards
const container = document.querySelector('[data-searchable]');
window.BenchmarkSearch.sortCards(container, 'title', 'asc');

// Get results count
const count = window.BenchmarkSearch.getSearchResultsCount();
```

### Utilities

```javascript
// Check if element is in viewport
const visible = window.LLMEvalHub.isElementInViewport(element);

// Add scroll animation
window.LLMEvalHub.addScrollAnimation('.card', 'fade-in', 100);

// Query parameters
window.LLMEvalHub.setQueryParameter('filter', 'evaluation');
const filter = window.LLMEvalHub.getQueryParameter('filter');

// Performance utilities
const debouncedFunc = window.LLMEvalHub.debounce(myFunction, 300);
const throttledFunc = window.LLMEvalHub.throttle(myFunction, 100);

// Re-initialize animations for dynamically added content
window.LLMEvalHub.reinitializeAnimations();
```

## Data Attributes for Features

### Search and Filter

```html
<!-- Make searchable -->
<div class="card" data-searchable>
  <h3>Card Title</h3>
  <p>Searchable content</p>
</div>

<!-- Category for filtering -->
<div class="card" data-category="framework">
  <!-- Card content -->
</div>

<!-- Filter buttons -->
<button data-filter="all">All</button>
<button data-filter="framework">Frameworks</button>
<button data-filter="benchmark">Benchmarks</button>

<!-- Category toggles -->
<button data-category-toggle="framework">Frameworks</button>
<button data-category-toggle="benchmark">Benchmarks</button>

<!-- Search input -->
<input type="search" data-search placeholder="Search...">
<button data-search-clear>Clear</button>
```

### Sorting

```html
<div class="card" data-sortable data-title="Framework A" data-difficulty="5">
  <!-- Sortable by these attributes -->
</div>
```

## Customization Tips

### Change Colors

Edit CSS custom properties in `css/style.css`:

```css
:root {
  --color-accent: #00d4ff;      /* Primary accent color */
  --color-primary: #6366f1;     /* Purple primary */
  --color-danger: #ff4757;      /* Error/danger color */
  --color-warning: #ffa502;     /* Warning color */
  --color-success: #2ed573;     /* Success color */
}

[data-theme="light"] {
  --color-accent: #0099cc;      /* Light mode accent */
  --color-text: #0a0e27;        /* Dark text on light bg */
  --color-bg: #ffffff;          /* White background */
}
```

### Adjust Spacing

```css
:root {
  --spacing-md: 1rem;           /* Base unit spacing */
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
}
```

### Change Fonts

```css
:root {
  --font-sans: 'Poppins', sans-serif;        /* Change sans-serif font */
  --font-mono: 'Roboto Mono', monospace;     /* Change monospace font */
}
```

## Accessibility Features

- Semantic HTML structure in your content
- ARIA labels on interactive elements
- Keyboard navigation (Tab, Enter, Space)
- Screen reader announcements for search results
- High contrast colors (WCAG AA compliant)
- Reduced motion support via prefers-reduced-motion
- Focus visible on interactive elements

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS 14+, Android Chrome)

## Performance Optimization

1. **Load CSS in head** - All three CSS files in `<head>`
2. **Load JS at end of body** - JavaScript files before closing `</body>`
3. **Use async/defer** - For third-party scripts
4. **Optimize images** - Use WebP with fallbacks
5. **Enable compression** - gzip for CSS/JS files
6. **Cache assets** - GitHub Pages handles automatic caching

## Common Patterns

### Filtering Section

```html
<section id="benchmarks" class="section">
  <div class="container">
    <h2 class="section-title">Benchmarks</h2>

    <!-- Filter buttons -->
    <div class="flex gap-md flex-wrap" style="margin-bottom: 2rem;">
      <button class="btn btn-primary active" data-filter="all">All</button>
      <button class="btn btn-secondary" data-filter="language">Language</button>
      <button class="btn btn-secondary" data-filter="reasoning">Reasoning</button>
    </div>

    <!-- Search -->
    <input type="search" data-search placeholder="Search benchmarks..."
           style="margin-bottom: 2rem; width: 100%; padding: 0.75rem;">

    <!-- Results -->
    <div class="grid-3">
      <div class="card fade-in" data-category="language" data-searchable>
        <h4 class="card-title">Benchmark Name</h4>
        <p class="card-description">Description</p>
        <span class="badge badge-category">Language</span>
      </div>
    </div>
  </div>
</section>
```

### Timeline Section

```html
<section class="section">
  <div class="container">
    <h2 class="section-title">Roadmap</h2>
    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-date">2024 Q2</div>
        <div class="timeline-title">Release v2.0</div>
        <div class="timeline-description">Major feature release</div>
      </div>
    </div>
  </div>
</section>
```

---

For more details, see README.md and the individual CSS/JS file comments.
