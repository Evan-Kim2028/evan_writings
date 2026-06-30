# Evan's Writings — Design System

This folder documents the visual design system for the site so future changes stay consistent.

## Color palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#0a0a0f` | Page background |
| `--bg-elevated` | `#12121a` | Footer, code blocks |
| `--surface` | `#181824` | Cards, elevated containers |
| `--surface-hover` | `#202032` | Card hover state |
| `--border` | `#2a2a3d` | Card borders, dividers |
| `--border-subtle` | `#1f1f2e` | Section dividers |
| `--text` | `#f0f0f5` | Headings, primary text |
| `--text-muted` | `#9ca3af` | Body text, descriptions |
| `--text-dim` | `#6b7280` | Metadata, captions |
| `--accent` | `#60a5fa` | Primary accent (blue) |
| `--accent-soft` | `rgba(96, 165, 250, 0.12)` | Subtle accent backgrounds |
| `--accent-glow` | `rgba(96, 165, 250, 0.25)` | Hero glow effects |
| `--secondary` | `#c084fc` | Secondary accent (purple) |
| `--secondary-soft` | `rgba(192, 132, 252, 0.12)` | Secondary glow |

## Typography

- **Body/UI:** system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue'
- **Code:** 'SF Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier
- **Headings:** 800 weight, tight letter-spacing, gradient text on hero and page headers

## Components

### Hero
- Large gradient headline
- Eyebrow badge with accent border
- Pill-style social links
- Radial glow accents behind content

### Cards
- Background: `--surface`
- Border: 1px solid `--border`
- Border-radius: 12px
- Shadow: subtle drop shadow
- Hover: lift up, border turns accent, deeper shadow

### Page header
- Back link above title
- Gradient headline
- Page description text
- Metadata and badges below

### Writing list cards
- Grid layout, min 300px
- Each item is a card with title + date
- Hover matches other cards

### Writing article card
- Article content wrapped in a card
- Body text uses muted color with `--text` for headings

## Spacing

- `--max-width`: 1000px
- Section gaps: 4–5rem
- Card padding: 1.5–1.75rem
- Article card padding: 2.5rem

## Accessibility

- Skip-to-content link on every page
- Visible `:focus-visible` outline (2px accent, 2px offset)
- Semantic HTML: `<header>`, `<nav>`, `<main>`, `<footer>`, `<article>`
- Descriptive link text and `aria-label` where helpful
- `theme-color` meta tag for mobile browsers
- `lang="en"` on `<html>`

## Responsive breakpoints

- Mobile: < 480px
- Tablet: < 768px
- Desktop: 768px+

Card grids collapse to single column on mobile. Navigation wraps on tablet and stacks vertically on small phones.

## Assets

- Favicon: `src/favicon.svg` (SVG, blue "E" on dark surface)
- 404 page: `src/404.njk`
- `robots.txt`: allows all, references sitemap
- Sitemap: `src/sitemap.xml.njk` with homepage, listings, and every writing
- Open Graph / Twitter Card meta tags on every page
