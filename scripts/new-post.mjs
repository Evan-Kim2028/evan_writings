#!/usr/bin/env node
// Scaffold a new writing post with correct frontmatter.
//
// Usage:
//   npm run new "My Great Title"
//   node scripts/new-post.mjs "My Great Title"
//   node scripts/new-post.mjs "My Great Title" --collection data
//   node scripts/new-post.mjs "My Great Title" --collection mev --source mirror
//
// Creates src/writings/<slug>.md with all required frontmatter fields,
// then suggests tags using the suggest-tags script.

import { writeFileSync, existsSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const WRITINGS_DIR = join(ROOT, 'src', 'writings');

// ---------- Parse args ----------
const args = process.argv.slice(2);
if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  console.log(`Usage: npm run new "Post Title" [--collection <name>] [--source <platform>] [--url <source_url>]

Options:
  --collection <name>    Collection name (latest, highlights, data, mev, defi, math). Default: latest
  --source <platform>    Source platform (mirror, paragraph, github, ethresear.ch, frontier.tech). Default: mirror
  --url <url>            Original source URL. Default: (none, fill in later)
  --date <YYYY-MM-DD>    Publication date. Default: today
  --no-tags              Skip tag suggestion step

Example:
  npm run new "Analying Uniswap V4 Hooks" --collection defi --source mirror --url https://mirror.xyz/...
`);
  process.exit(0);
}

const title = args[0];
let collection = 'latest';
let sourcePlatform = 'mirror';
let sourceUrl = '';
let date = new Date().toISOString().split('T')[0];
let suggestTags = true;

for (let i = 1; i < args.length; i++) {
  switch (args[i]) {
    case '--collection': collection = args[++i]; break;
    case '--source': sourcePlatform = args[++i]; break;
    case '--url': sourceUrl = args[++i]; break;
    case '--date': date = args[++i]; break;
    case '--no-tags': suggestTags = false; break;
  }
}

// ---------- Generate slug ----------
function slugify(text) {
  return String(text)
    .toLowerCase()
    .replace(/['"]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-+/g, '-');
}

const slug = slugify(title);
const filepath = join(WRITINGS_DIR, `${slug}.md`);

if (existsSync(filepath)) {
  console.error(`Error: File already exists: ${filepath}`);
  console.error('Use a different title or edit the existing file.');
  process.exit(1);
}

// ---------- Generate frontmatter ----------
const frontmatter = [
  '---',
  `title: "${title}"`,
  `date: "${date}"`,
  `collection: ${collection}`,
  'tags:',
  '  - writing',
  `  - ${collection}`,
  `  - ${sourcePlatform}`,
  sourceUrl ? `source_url: ${sourceUrl}` : 'source_url: ',
  `source_platform: ${sourcePlatform}`,
  `slug: ${slug}`,
  'description: ""',
  '---',
  '',
  `# ${title}`,
  '',
  'Write your content here.',
  '',
].join('\n');

writeFileSync(filepath, frontmatter);
console.log(`Created: ${filepath}`);
console.log(`\nNext steps:`);
console.log(`  1. Write your content in the file`);
console.log(`  2. Fill in the description field (140-165 chars, keyword-first)`);
console.log(`  3. Fill in the source_url if not set`);
console.log(`  4. Run: npm run suggest-tags  (to auto-suggest topical tags)`);
console.log(`  5. Run: npm run test  (to verify everything renders)`);

// ---------- Optionally suggest tags ----------
if (suggestTags) {
  console.log(`\n${'='.repeat(60)}`);
  console.log('Tag suggestions (based on title only — run again after writing content for better suggestions):');
  console.log(`${'='.repeat(60)}\n`);
  try {
    execSync(`node "${join(__dirname, 'suggest-tags.mjs')}"`, {
      stdio: 'inherit',
      cwd: ROOT,
    });
  } catch {
    console.log('(Tag suggestion skipped — run npm run suggest-tags after writing content)');
  }
}
