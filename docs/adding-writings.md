# Adding a new writing

Use the template at `src/_templates/writing.md` as a starting point for every new post.

## Quick start

1. Copy `src/_templates/writing.md` to `src/writings/<slug>.md`.
2. Fill in the frontmatter.
3. Run `npm run build` and `npm run serve` to preview.
4. Commit and push.

## Frontmatter reference

| Field | Required | Notes |
|-------|----------|-------|
| `title` | Yes | Article title. Used in page title, cards, and headers. |
| `date` | Yes | `YYYY-MM-DD`. Used for sorting and the sitemap. |
| `collection` | Yes | One of: `latest`, `highlights`, `data`, `mev`, `defi`, `math`. |
| `description` | Recommended | 1–2 sentences for search engines and social previews. |
| `tags` | Yes | Always include `writing` and the collection name. Add the source platform if you want. |
| `source_url` | Optional | Original URL if the post was first published elsewhere. |
| `source_platform` | Optional | `paragraph`, `mirror`, `ethresear.ch`, `github`, `frontier.tech`. |
| `slug` | Yes | Must match the filename (`src/writings/<slug>.md`). Used for stable URLs. |

## Slug rules

- Lowercase letters, numbers, and hyphens only.
- No spaces or special characters.
- Keep it stable: changing the slug breaks existing links.

## Image guidelines

- Save images to `src/assets/images/`.
- Reference them with `/assets/images/<filename>` in Markdown.
- Add alt text: `![Descriptive alt text](/assets/images/filename.png)`.

## Markdown tips

- Use a `## TL;DR / Summary` section near the top for the homepage excerpt.
- Keep line length reasonable (under 100 characters) for diffs.
- Code blocks with language tags get syntax highlighting.
- Wide tables automatically scroll horizontally on mobile.
