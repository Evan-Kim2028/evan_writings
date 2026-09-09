# Evan's Writings — Design System

Editorial, light-first, figures-as-hero. Prototypes that drove this system live alongside this file (`index.html`, `prototype.html`).

## Tokens (`src/styles.css`)

Theme is set by `data-theme` on `<html>` (light default, follows `prefers-color-scheme`, toggle persists in `localStorage`, no-flash init script in `base.njk`).

| Token | Light | Dark | Usage |
|---|---|---|---|
| `--bg` | `#fbfbf9` | `#0f1013` | Page |
| `--bg-2` | `#f2f1ec` | `#16181d` | Figure boxes, code, inputs |
| `--text` | `#1a1a1a` | `#e8e6e1` | Headings, body |
| `--text-2` | `#4b4b4b` | `#b3b0a8` | Secondary text |
| `--text-3` | `#8a8a85` | `#6f6d68` | Meta, captions |
| `--line` | `#e3e2dc` | `#26282e` | Rules, borders |
| `--accent` | `#1f5fbf` | `#7aa7ff` | Links, chart marks |
| `--accent-2` | `#b6541e` | `#f19a5b` | Kickers |
| `--hi` | `#fff3d6` | `#2a2410` | `td.best` highlight |

## Typography

- Body/UI: Inter, 17px, line-height 1.6, prose column `68ch`
- Display/headings: Newsreader (serif), weight 500, tight tracking
- Code: JetBrains Mono
- Fonts load from Google Fonts with `display=swap`.

## Layout

- Page width `--wide: 1180px`.
- Article: 200px sticky left rail (TOC + back link) and a content column. Prose is capped at `68ch`; `figure.wide` fills the content column.
- Home: intro, Latest (lead + two), Selected (= `highlights` collection), Archive grouped by year with collection filters.

## Article content conventions

- Markdown images become `<figure class="wide">`; an immediately following *italic paragraph* becomes the `<figcaption>`.
- Markdown tables become sortable (`table.sortable`) inside a `.fig-box`. Mark the best cell with `<td class="best">` in raw HTML if needed.
- Math: `$…$` and `$$…$$` rendered at build time with KaTeX.
- Interactive charts: `{% chart "assets/charts/name.json", "<b>Figure N.</b> caption" %}`. The JSON is `{ data, layout }` in Plotly format. Colors omitted from the spec are filled from theme tokens and redrawn on theme toggle. Plotly is loaded from CDN only on pages that use a chart.

## Motion

`.reveal` fade-up on intersection, reading-progress bar, hover lifts. All disabled under `prefers-reduced-motion`.
