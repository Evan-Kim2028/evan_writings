# evan_writings

A public archive of Evan Kim's writings on DeFi, data, MEV, and math.

- **Site:** https://Evan-Kim2028.github.io/evan_writings
- **Source:** https://github.com/Evan-Kim2028/evan_writings

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## MCP server

The `mcp/` directory contains a local MCP server for searching the writings.

```bash
npm run mcp:build
npm run mcp:run
```

## Adding a new writing

1. Create a new Markdown file in `src/writings/`.
2. Add YAML frontmatter: `title`, `date`, `collection`, `tags`, `source_url`, `source_platform`, `slug`.
3. Run `npm run build` and verify the site renders.

## License

MIT
