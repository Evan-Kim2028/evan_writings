# Spec: evan_writings

## Assumptions

1. GitHub username is `Evan-Kim2028`; the new repo will be `evan_writings`.
2. Local development directory is `/home/evan/Documents/evan_writings`.
3. Static site generator is **Eleventy (11ty) v3** with Nunjucks templates — chosen because it is JavaScript-native, supports Markdown with frontmatter, and is simple to deploy on GitHub Pages.
4. No custom domain in this first pass; the site will live at `https://Evan-Kim2028.github.io/evan_writings`.
5. Content migration starts from the existing index at `https://paragraph.com/@evandekim/past-writings`; full-text bodies will be pulled where the source platform allows it, otherwise we link to the canonical URL.
6. The MCP server is local-only, implemented in TypeScript, and searches over a generated `llms-full.txt` index.
7. The first milestone is a working site with all writings indexed and a searchable MCP; polish and design are out of scope for this pass.

→ Correct me if any of these are wrong.

## Objective

Build a self-hosted, GitHub Pages-backed blog and writings archive that:

- Stores all past writings in a public GitHub repository (`evan_writings`).
- Renders them as a clean, navigable static site.
- Preserves original canonical links.
- Provides an MCP server so people (and the user) can search through all writings with natural-language queries.

Success criteria:

- [ ] `https://Evan-Kim2028.github.io/evan_writings` loads and lists all writings.
- [ ] Each writing has its own page with title, date, tags, collection, and body or canonical link.
- [ ] Writings are grouped into collections: `Latest`, `Highlights`, `Data`, `MEV`, `DeFi`, `Math`.
- [ ] A local MCP server can `list_writings`, `search_writings`, and `get_writing`.
- [ ] The repo is public on GitHub under `Evan-Kim2028/evan_writings`.
- [ ] The local directory `/home/evan/Documents/evan_writings` can be developed and built independently.

## Tech Stack

- **Static site generator:** Eleventy 3.x (Node.js 20+)
- **Templating:** Nunjucks
- **Styling:** Plain CSS (no build pipeline)
- **Content format:** Markdown with YAML frontmatter
- **Search index:** `llms-full.txt` generated at build time
- **MCP server:** TypeScript + `@modelcontextprotocol/sdk` (stdio transport)
- **Package manager:** npm
- **CI/CD:** GitHub Actions for Pages deployment

## Commands

```bash
# Development
npm run dev          # 11ty serve with watch
npm run build        # Build static site into _site
npm run clean        # Remove _site

# MCP server
npm run mcp:build    # Compile MCP server
npm run mcp:run      # Run MCP server over stdio

# Repository
npm run deploy       # Placeholder for manual gh-pages trigger
```

## Project Structure

```
/home/evan/Documents/evan_writings
├── SPEC.md
├── README.md
├── package.json
├── .eleventy.js
├── .eleventyignore
├── .gitignore
├── .github
│   └── workflows
│       └── pages.yml        # Build and deploy to GitHub Pages
├── src
│   ├── _includes
│   │   ├── base.njk         # Base layout
│   │   ├── writing.njk      # Single writing layout
│   │   └── collection.njk     # Collection listing layout
│   ├── _data
│   │   └── collections.js     # Collection metadata
│   ├── index.njk            # Home page
│   ├── collections.njk      # All collections overview
│   ├── writings.njk         # All writings listing
│   ├── llms-full.txt.njk    # Search index (not rendered as HTML)
│   ├── llms.txt.njk         # Lightweight index
│   ├── styles.css           # Site styles
│   └── writings             # One .md file per writing
│       └── ...
├── mcp
│   ├── package.json
│   ├── tsconfig.json
│   ├── src
│   │   ├── index.ts
│   │   ├── search.ts
│   │   └── types.ts
│   └── dist
│       └── ...
└── scripts
    ├── scrape.py            # Scrape index and fetch post bodies
    └── migrate.py           # Migrate/update existing files
```

## Code Style

- Markdown frontmatter is lowercase with underscores:

  ```markdown
  ---
  title: "Sui NFT Analytics"
  date: 2025-02-01
  collection: data
  tags: ["sui", "nft", "analytics"]
  source_url: "https://paragraph.xyz/@evandekim/sui-nft-collection-analytics"
  source_platform: "paragraph"
  slug: "sui-nft-collection-analytics"
  ---
  ```

- Nunjucks templates use 2-space indentation.
- TypeScript uses strict mode, single quotes, and trailing commas.
- Python scripts are plain, no external frameworks unless required.

## Testing Strategy

- Manual verification that the site builds and renders.
- Manual verification that the MCP server responds to `list_writings`, `search_writings`, and `get_writing`.
- No unit tests in this first pass; add them if the MCP server grows.

## Boundaries

- **Always do:** Run `npm run build` before committing, keep frontmatter consistent, preserve original URLs.
- **Ask first:** Change the site generator, add a custom domain, change the MCP transport, add heavy dependencies.
- **Never do:** Commit secrets, delete original canonical content, force-push to `main`.

## Success Criteria

See Objective checklist.

## Open Questions

1. Do you want full post bodies pulled into the repo, or is a curated index with links to originals acceptable for now?
2. Should the MCP server be configured for Claude Desktop, or just run as a standalone stdio server?
3. Do you want to bring external pieces (ethresear.ch, GitHub PDFs, Frontier.tech) into the repo as Markdown or leave them as canonical links?
