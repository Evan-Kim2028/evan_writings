#!/usr/bin/env node
// scripts/dark-figures.mjs
// Usage: node scripts/dark-figures.mjs <input.html> <output.html>
//
// Applies a fixed light->dark palette remap to an HTML file's inline colors
// and writes the result. If `playwright` is resolvable, also renders each
// `figure[id]` element in the output HTML to `<out>-<id>.png` at
// deviceScaleFactor 1. Otherwise prints an instruction for manual PNG
// rendering.

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

const PALETTE = {
  '#ffffff': '#14181f',
  '#fff': '#14181f',
  '#ececec': '#0e1116',
  '#d9d9d9': '#2a3140',
  '#1a1a1a': '#e8eaf0',
  '#222': '#e8eaf0',
  '#333': '#d0d4dc',
  '#555': '#b8bec9',
  '#666': '#9aa3b2',
  '#888': '#8a93a3',
  '#ddd': '#2a3140',
  '#d6d6d6': '#2a3140',
  '#bbb': '#4a5262',
  '#444': '#c8cdd6',
  '#eef1f5': '#1e2633',
  '#8a97a8': '#6f7d93',
  '#fbe9e7': '#3a1f1f',
  '#e6f3ea': '#17301f',
  '#fff7dd': '#332b14',
  '#e0b84a': '#c9a24a',
  '#8a5a00': '#e2b95c',
  '#b3261e': '#ff6b5e',
  '#1b6e3a': '#5fd39a',
  '#f6f6f4': '#1a1f28',
};

function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function buildPaletteRegex() {
  // Longest keys first so e.g. #ffffff is matched before #fff.
  const keys = Object.keys(PALETTE).sort((a, b) => b.length - a.length);
  const alternation = keys.map(escapeRegex).join('|');
  // Negative lookahead: do not match when followed by another hex digit
  // (prevents #fff from partially matching inside a longer hex it wasn't
  // ordered ahead of, and prevents matching a prefix of an unmapped color).
  return new RegExp(`(${alternation})(?![0-9a-fA-F])`, 'gi');
}

function applyPalette(html) {
  const re = buildPaletteRegex();
  let out = html.replace(re, (match) => {
    const key = match.toLowerCase();
    return PALETTE[key] !== undefined ? PALETTE[key] : match;
  });
  // Add fill="#e8eaf0" to every <svg tag so default text is light.
  out = out.replace(/<svg(\s|>)/gi, '<svg fill="#e8eaf0"$1');
  return out;
}

async function renderFigurePngs(outPath) {
  let playwrightPath;
  try {
    playwrightPath = require.resolve('playwright');
  } catch (e) {
    playwrightPath = null;
  }

  if (!playwrightPath) {
    console.log(
      `[dark-figures] playwright is not installed — skipping PNG rendering.\n` +
      `[dark-figures] To render figure[id] elements to <out>-<id>.png, run:\n` +
      `  npm install --save-dev playwright && npx playwright install chromium\n` +
      `  node scripts/dark-figures.mjs <input.html> <output.html>`
    );
    return;
  }

  const { chromium } = require('playwright');
  const outAbs = path.resolve(outPath);
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ deviceScaleFactor: 1 });
    await page.goto('file://' + outAbs);
    const figures = await page.$$('figure[id]');
    if (figures.length === 0) {
      console.log('[dark-figures] no figure[id] elements found — nothing to render.');
    }
    const base = outAbs.replace(/\.html?$/i, '');
    for (const fig of figures) {
      const id = await fig.getAttribute('id');
      const pngPath = `${base}-${id}.png`;
      await fig.screenshot({ path: pngPath });
      console.log(`[dark-figures] rendered ${pngPath}`);
    }
  } finally {
    await browser.close();
  }
}

async function main() {
  const [, , inputPath, outputPath] = process.argv;
  if (!inputPath || !outputPath) {
    console.error('Usage: node scripts/dark-figures.mjs <input.html> <output.html>');
    process.exit(1);
  }

  const html = fs.readFileSync(inputPath, 'utf8');
  const dark = applyPalette(html);
  fs.writeFileSync(outputPath, dark);
  console.log(`[dark-figures] wrote ${outputPath}`);

  await renderFigurePngs(outputPath);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
