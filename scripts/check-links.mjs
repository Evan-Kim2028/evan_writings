#!/usr/bin/env node
// External link checker for evan_writings.
//
// Scans all writing markdown files for external URLs and checks each
// for HTTP errors (404, 500, etc.) using HEAD requests with GET fallback.
//
// Usage:
//   node scripts/check-links.mjs              # check all links
//   node scripts/check-links.mjs --timeout 10 # 10s timeout per link
//   node scripts/check-links.mjs --verbose    # show all links, not just failures
//
// Exits non-zero if any broken links are found.

import { readdirSync, readFileSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const WRITINGS_DIR = join(ROOT, 'src', 'writings');

const verbose = process.argv.includes('--verbose');
const timeoutArg = process.argv[process.argv.indexOf('--timeout') + 1];
const TIMEOUT_MS = (parseInt(timeoutArg, 10) || 10) * 1000;

// URLs to skip (known rate-limited or auth-walled destinations that
// always return 403/429 to bots but work fine for humans)
const SKIP_PATTERNS = [
  /^https?:\/\/(?:www\.)?(?:twitter|x)\.com\//,    // X/Twitter blocks bots
  /^https?:\/\/(?:www\.)?reddit\.com\//,            // Reddit blocks bots
  /^https?:\/\/(?:www\.)?medium\.com\//,            // Medium blocks bots
  /^https?:\/\/(?:www\.)?linkedin\.com\//,          // LinkedIn blocks bots
  /^https?:\/\/dune\.com\//,                        // Dune blocks bots
  /^https?:\/\/(?:www\.)?opensea\.com\//,           // OpenSea blocks bots
  /^https?:\/\/(?:www\.)?youtube\.com\//,           // YouTube blocks bots
  /^https?:\/\/(?:www\.)?youtu\.be\//,              // YouTube short links
  /^https?:\/\/(?:www\.)?warpcast\.com\//,          // Warpcast blocks bots
  /^https?:\/\/(?:www\.)?paragraph\.xyz\//,         // Paragraph blocks bots
  /^https?:\/\/(?:www\.)?mirror\.xyz\//,            // Mirror blocks bots
  /^https?:\/\/(?:www\.)?ethresear\.ch\//,          // ethresear.ch blocks bots
  /^https?:\/\/(?:www\.)?frontier\.tech\//,         // frontier.tech blocks bots
  /^https?:\/\/(?:www\.)?github\.com\//,            // GitHub blocks bots
  /^https?:\/\/(?:www\.)?etherscan\.io\//,          // Etherscan blocks bots
  /^https?:\/\/(?:www\.)?solscan\.io\//,            // Solscan blocks bots
  /^https?:\/\/(?:www\.)?suiexplorer\.com\//,       // Sui explorer blocks bots
  /^https?:\/\/(?:www\.)?suiscan\.xyz\//,           // Suiscan blocks bots
];

function shouldSkip(url) {
  return SKIP_PATTERNS.some((p) => p.test(url));
}

// Extract all URLs from markdown content (excluding frontmatter)
function extractUrls(filePath) {
  const raw = readFileSync(filePath, 'utf8');
  // Strip frontmatter
  const body = raw.startsWith('---') ? raw.slice(raw.indexOf('\n---', 3) + 4) : raw;
  // Match URLs in markdown links, plain text, and image src
  const urlSet = new Set();
  // Markdown links: [text](url) and [text]: url
  for (const m of body.matchAll(/\[([^\]]*)\]\(([^)]+)\)/g)) {
    const url = m[2].split(/\s/)[0]; // handle "url title" format
    if (/^https?:\/\//.test(url)) urlSet.add(url);
  }
  for (const m of body.matchAll(/\[([^\]]+)\]:\s*(https?:\/\/[^\s]+)/g)) {
    urlSet.add(m[2]);
  }
  // Plain URLs
  for (const m of body.matchAll(/(?<![!\[(])(https?:\/\/[^\s)\]"']+)/g)) {
    urlSet.add(m[1]);
  }
  // Image URLs: ![alt](url)
  for (const m of body.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)) {
    if (/^https?:\/\//.test(m[1])) urlSet.add(m[1]);
  }
  return [...urlSet];
}

async function checkUrl(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    // Try HEAD first (lighter), fall back to GET if not supported
    let res = await fetch(url, {
      method: 'HEAD',
      signal: controller.signal,
      redirect: 'follow',
      headers: { 'User-Agent': 'evan-writings-link-checker/1.0' },
    });
    if (res.status === 405 || res.status === 403) {
      // Some servers reject HEAD — try GET
      clearTimeout(timer);
      const controller2 = new AbortController();
      const timer2 = setTimeout(() => controller2.abort(), TIMEOUT_MS);
      res = await fetch(url, {
        method: 'GET',
        signal: controller2.signal,
        redirect: 'follow',
        headers: { 'User-Agent': 'evan-writings-link-checker/1.0' },
      });
      clearTimeout(timer2);
    } else {
      clearTimeout(timer);
    }
    return { status: res.status, ok: res.ok, redirected: res.redirected };
  } catch (e) {
    clearTimeout(timer);
    return { status: 0, ok: false, error: e.message };
  }
}

// ---------- Main ----------
async function main() {
  const mdFiles = readdirSync(WRITINGS_DIR)
    .filter((f) => f.endsWith('.md'))
    .map((f) => join(WRITINGS_DIR, f));

  // Collect all unique URLs with their source files
  const urlToFiles = new Map();
  for (const mdFile of mdFiles) {
    const urls = extractUrls(mdFile);
    for (const url of urls) {
      if (!urlToFiles.has(url)) urlToFiles.set(url, []);
      urlToFiles.get(url).push(basename(mdFile));
    }
  }

  const allUrls = [...urlToFiles.keys()];
  const checkableUrls = allUrls.filter((u) => !shouldSkip(u));
  const skippedUrls = allUrls.filter((u) => shouldSkip(u));

  console.log(`\nLink Checker Report`);
  console.log(`${'='.repeat(60)}`);
  console.log(`Total unique URLs: ${allUrls.length}`);
  console.log(`URLs to check: ${checkableUrls.length}`);
  console.log(`URLs skipped (known bot-blocked): ${skippedUrls.length}`);
  console.log(`${'='.repeat(60)}\n`);

  const broken = [];
  const warnings = [];
  let checked = 0;

  // Check URLs with limited concurrency (5 at a time)
  const BATCH_SIZE = 5;
  for (let i = 0; i < checkableUrls.length; i += BATCH_SIZE) {
    const batch = checkableUrls.slice(i, i + BATCH_SIZE);
    const results = await Promise.all(
      batch.map(async (url) => {
        const result = await checkUrl(url);
        checked++;
        const files = urlToFiles.get(url);
        return { url, files, ...result };
      })
    );

    for (const r of results) {
      if (r.error) {
        broken.push(r);
        console.log(`  ✗ ERROR  ${r.url}`);
        console.log(`    ${r.error}`);
        console.log(`    in: ${r.files.join(', ')}`);
      } else if (r.status === 404) {
        broken.push(r);
        console.log(`  ✗ 404    ${r.url}`);
        console.log(`    in: ${r.files.join(', ')}`);
      } else if (r.status >= 400 && r.status < 500) {
        warnings.push(r);
        if (verbose) console.log(`  ⚠ ${r.status}   ${r.url}`);
      } else if (r.status >= 500) {
        broken.push(r);
        console.log(`  ✗ ${r.status}   ${r.url}`);
        console.log(`    in: ${r.files.join(', ')}`);
      } else if (verbose) {
        console.log(`  ✓ ${r.status}   ${r.url}`);
      }
    }

    // Progress
    process.stdout.write(`\r  Progress: ${checked}/${checkableUrls.length} checked...`);
  }
  console.log('\n');

  // Summary
  console.log(`${'='.repeat(60)}`);
  console.log(`Summary:`);
  console.log(`  Checked: ${checked}`);
  console.log(`  Broken: ${broken.length}`);
  console.log(`  Warnings: ${warnings.length}`);
  console.log(`  Skipped: ${skippedUrls.length}`);

  if (skippedUrls.length > 0 && verbose) {
    console.log(`\nSkipped URLs (known to block bots):`);
    for (const url of skippedUrls.slice(0, 10)) {
      console.log(`  ⊘ ${url}`);
    }
    if (skippedUrls.length > 10) console.log(`  ... and ${skippedUrls.length - 10} more`);
  }

  if (broken.length > 0) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`BROKEN LINKS (${broken.length}):`);
    for (const r of broken) {
      const status = r.status || 'ERR';
      console.log(`  ${status} ${r.url}`);
      console.log(`       in: ${r.files.join(', ')}`);
    }
    process.exit(1);
  }

  console.log(`\nOK — no broken links found.`);
  process.exit(0);
}

main().catch((e) => {
  console.error('Fatal error:', e);
  process.exit(1);
});
