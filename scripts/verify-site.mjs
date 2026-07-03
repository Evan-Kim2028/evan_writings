#!/usr/bin/env node
// Post-build verification for the evan_writings static site.
//
// Run after `npm run build`. Exits non-zero on any failure so CI blocks.
//
// Checks (against _site/):
//   1. Required index pages exist and are non-empty
//   2. Every writing HTML has <title>, meta description, OG/Twitter tags
//   3. Every <img src> resolves to a real file under _site/
//   4. Every internal <a href> (root-relative, same-site) resolves to a file
//   5. Every in-page anchor <a href="#id"> resolves to an element id in the doc
//   6. Every TOC link (.toc-link) anchor resolves to a heading id
//   7. Every writing source .md has required frontmatter
//      (title, date, collection, slug, source_url)
//   8. Sitemap <loc> URLs all resolve to built files
//
// No external dependencies — uses node:fs, node:path, node:url only.

import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join, relative, dirname, basename, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const SITE = join(ROOT, '_site');
const WRITINGS_SRC = join(ROOT, 'src', 'writings');
const PATH_PREFIX = '/evan_writings'; // matches .eleventy.js pathPrefix

const errors = [];
const warnings = [];
const err = (msg) => errors.push(msg);
const warn = (msg) => warnings.push(msg);

function walk(dir, predicate = () => true) {
  const out = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full, predicate));
    else if (predicate(full)) out.push(full);
  }
  return out;
}

function stripQueryHash(p) {
  return p.split('#')[0].split('?')[0];
}

// Resolve a root-relative URL path like "/evan_writings/writings/foo/" to
// a filesystem path under _site. Directory URLs map to index.html.
function resolveSitePath(urlPath) {
  let p = stripQueryHash(urlPath);
  // Strip the pathPrefix (the site is served from /evan_writings on Pages).
  if (p.startsWith(PATH_PREFIX)) p = p.slice(PATH_PREFIX.length);
  if (!p.startsWith('/')) p = '/' + p;
  if (p === '/' || p === '') return join(SITE, 'index.html');
  // Directory URL -> index.html
  if (p.endsWith('/')) return join(SITE, p, 'index.html');
  // If it has no extension, treat as directory
  if (!extname(p)) return join(SITE, p, 'index.html');
  return join(SITE, p);
}

// ---------- 1. Required index pages ----------
const requiredPages = [
  'index.html',
  'writings/index.html',
  'collections/index.html',
  'sitemap.xml',
  'robots.txt',
  'llms-full.txt',
  'feed.xml',
  'assets/og-default.png',
];
for (const rel of requiredPages) {
  const full = join(SITE, rel);
  if (!existsSync(full)) err(`Missing required page: ${rel}`);
  else if (statSync(full).size === 0) err(`Empty required page: ${rel}`);
}

// ---------- Gather all HTML files ----------
const htmlFiles = walk(SITE, (f) => f.endsWith('.html'));
if (htmlFiles.length === 0) err('No HTML files built in _site/');

// Track all in-site anchor targets we've seen for cross-page anchor checks
// (not strictly needed; we do per-doc anchor checks below).

// ---------- 2-6. Per-HTML checks ----------
const isWritingPage = (f) => f.startsWith(join(SITE, 'writings') + '/');
let checkedPages = 0;
for (const htmlFile of htmlFiles) {
  checkedPages++;
  const rel = relative(SITE, htmlFile);
  const raw = readFileSync(htmlFile, 'utf8');
  if (raw.length === 0) {
    err(`Empty HTML: ${rel}`);
    continue;
  }

  const isWriting = isWritingPage(htmlFile) && rel !== 'writings/index.html';

  // 2. Required meta on writing pages (and the home page)
  if (isWriting || rel === 'index.html') {
    if (!/<title>[^<]+<\/title>/.test(raw)) err(`Missing <title>: ${rel}`);
    if (!/<meta name="description" content="[^"]+">/.test(raw)) err(`Missing meta description: ${rel}`);
    if (!/property="og:title"/.test(raw)) err(`Missing og:title: ${rel}`);
    if (!/property="og:description"/.test(raw)) err(`Missing og:description: ${rel}`);
    if (!/property="og:image"/.test(raw)) err(`Missing og:image: ${rel}`);
    if (!/property="og:url"/.test(raw)) err(`Missing og:url: ${rel}`);
    if (!/name="twitter:card"/.test(raw)) err(`Missing twitter:card: ${rel}`);
    if (!/name="twitter:image"/.test(raw)) err(`Missing twitter:image: ${rel}`);
    if (!/rel="canonical"/.test(raw)) err(`Missing canonical link: ${rel}`);
    if (!/application\/ld\+json/.test(raw)) err(`Missing JSON-LD structured data: ${rel}`);
  }

  // 2b. Article-specific OG tags on writing pages
  if (isWriting) {
    if (!/property="article:published_time"/.test(raw)) err(`Missing article:published_time: ${rel}`);
    if (!/property="article:author"/.test(raw)) err(`Missing article:author: ${rel}`);
    if (!/property="article:section"/.test(raw)) err(`Missing article:section: ${rel}`);
    // Verify JSON-LD contains an Article node
    if (!/"@type":\s*"Article"/.test(raw)) err(`Missing Article JSON-LD schema: ${rel}`);
  }

  // 2c. Verify OG image URL is absolute (https://)
  const ogImgMatch = raw.match(/property="og:image" content="([^"]+)"/);
  if (ogImgMatch && !/^https?:\/\//.test(ogImgMatch[1])) {
    err(`og:image is not an absolute URL: ${ogImgMatch[1]} in ${rel}`);
  }

  // 2d. Verify JSON-LD is valid JSON (parse the script block)
  const jsonLdMatch = raw.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
  if (jsonLdMatch) {
    try {
      JSON.parse(jsonLdMatch[1].trim());
    } catch (e) {
      err(`Invalid JSON-LD in ${rel}: ${e.message}`);
    }
  }

  // Collect all element ids in the document
  const idSet = new Set();
  for (const m of raw.matchAll(/\bid="([^"]+)"/g)) idSet.add(m[1]);

  // 3. Images
  for (const m of raw.matchAll(/<img[^>]+src="([^"]+)"/g)) {
    const src = m[1];
    if (/^https?:\/\//.test(src) || src.startsWith('data:')) continue;
    const resolved = resolveSitePath(src);
    if (!existsSync(resolved)) err(`Broken image: ${src} in ${rel}`);
  }

  // 4-5. Links
  for (const m of raw.matchAll(/<a[^>]+href="([^"]+)"/g)) {
    const href = m[1];
    if (/^https?:\/\//.test(href) || href.startsWith('mailto:') || href.startsWith('tel:')) continue;
    if (href === '#main' || href === '#') continue;

    if (href.startsWith('#')) {
      // In-page anchor
      const id = href.slice(1);
      if (!idSet.has(id)) err(`Broken in-page anchor: ${href} in ${rel}`);
      continue;
    }

    if (href.startsWith('/')) {
      // Root-relative. Could be /evan_writings/... or /assets/... (legacy).
      const resolved = resolveSitePath(href);
      if (!existsSync(resolved)) err(`Broken internal link: ${href} in ${rel}`);
      continue;
    }

    // Relative link — resolve against the doc's directory.
    const resolved = join(dirname(htmlFile), href.split('#')[0].split('?')[0]);
    if (!existsSync(resolved)) err(`Broken relative link: ${href} in ${rel}`);
  }

  // 6. TOC anchors specifically (class and href can appear in any order)
  const tocAnchorRe = /<a\b[^>]*\bclass="toc-link[^"]*"[^>]*>/g;
  let tocMatch;
  let tocCount = 0;
  while ((tocMatch = tocAnchorRe.exec(raw)) !== null) {
    const tag = tocMatch[0];
    const hrefMatch = tag.match(/href="#([^"]+)"/);
    if (!hrefMatch) {
      err(`TOC link without href anchor: ${tag} in ${rel}`);
      continue;
    }
    tocCount++;
    const id = hrefMatch[1];
    if (!idSet.has(id)) err(`Broken TOC anchor: #${id} in ${rel}`);
  }
  // If there are H2/H3 in the writing body but no TOC was emitted, that's
  // fine for <2 headings; warn only when many headings exist without a TOC.
  if (isWriting) {
    const h2h3 = raw.match(/<h[23][^>]*>/g) || [];
    if (h2h3.length >= 2 && tocCount === 0) {
      warn(`Writing with ${h2h3.length} H2/H3 but no TOC: ${rel}`);
    }
  }
}

// ---------- 7. Frontmatter on writing sources ----------
const mdFiles = readdirSync(WRITINGS_SRC)
  .filter((f) => f.endsWith('.md'))
  .map((f) => join(WRITINGS_SRC, f));
const requiredFrontmatter = ['title', 'date', 'collection', 'slug', 'source_url'];
for (const md of mdFiles) {
  const raw = readFileSync(md, 'utf8');
  if (!raw.startsWith('---')) {
    err(`Missing frontmatter delimiters: ${relative(ROOT, md)}`);
    continue;
  }
  const end = raw.indexOf('\n---', 3);
  if (end === -1) {
    err(`Unclosed frontmatter: ${relative(ROOT, md)}`);
    continue;
  }
  const fm = raw.slice(3, end);
  for (const key of requiredFrontmatter) {
    const re = new RegExp(`^${key}:\\s+\\S`, 'm');
    if (!re.test(fm)) err(`Missing frontmatter \`${key}\`: ${relative(ROOT, md)}`);
  }
}

// ---------- 8. Sitemap URLs resolve ----------
const sitemapPath = join(SITE, 'sitemap.xml');
if (existsSync(sitemapPath)) {
  const sm = readFileSync(sitemapPath, 'utf8');
  const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim());
  for (const loc of locs) {
    try {
      const u = new URL(loc);
      // Only check same-origin (Pages) URLs.
      if (!u.pathname.startsWith(PATH_PREFIX) && u.pathname !== '/') continue;
      const resolved = resolveSitePath(u.pathname);
      if (!existsSync(resolved)) err(`Sitemap loc does not resolve: ${loc}`);
    } catch {
      err(`Sitemap loc is not a valid URL: ${loc}`);
    }
  }
}

// ---------- Report ----------
console.log(`\nVerified ${checkedPages} HTML pages, ${mdFiles.length} writing sources.`);
if (warnings.length) {
  console.log(`\nWarnings (${warnings.length}):`);
  for (const w of warnings) console.log(`  ⚠ ${w}`);
}
if (errors.length) {
  console.error(`\nFailed with ${errors.length} error(s):`);
  for (const e of errors) console.error(`  ✗ ${e}`);
  process.exit(1);
}
console.log(`\nOK — no rendering errors.`);
process.exit(0);
