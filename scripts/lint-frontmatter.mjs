#!/usr/bin/env node
// Frontmatter linter for writing markdown files.
//
// Called by lint-staged on staged .md files. Validates that each writing
// has all required frontmatter fields with correct types and formats.
//
// Usage:
//   node scripts/lint-frontmatter.mjs <file1.md> [file2.md ...]
//
// Exits non-zero if any file has invalid frontmatter.

import { readFileSync } from 'node:fs';

const REQUIRED_FIELDS = [
  { name: 'title', type: 'string', test: (v) => typeof v === 'string' && v.length > 0 },
  { name: 'date', type: 'string', test: (v) => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v) },
  { name: 'collection', type: 'string', test: (v) => ['latest', 'highlights', 'data', 'mev', 'defi', 'math'].includes(v) },
  { name: 'tags', type: 'array', test: (v) => Array.isArray(v) && v.includes('writing') },
  { name: 'source_url', type: 'string', test: (v) => typeof v === 'string' && v.length > 0 },
  { name: 'source_platform', type: 'string', test: (v) => ['mirror', 'paragraph', 'github', 'ethresear.ch', 'frontier.tech'].includes(v) },
  { name: 'slug', type: 'string', test: (v) => typeof v === 'string' && /^[a-z0-9-]+$/.test(v) },
  { name: 'description', type: 'string', test: (v) => typeof v === 'string' && v.length >= 50 && v.length <= 200 },
];

function extractFrontmatter(raw) {
  if (!raw.startsWith('---')) return null;
  const end = raw.indexOf('\n---', 3);
  if (end === -1) return null;
  return raw.slice(3, end);
}

function parseFrontmatter(fm) {
  const result = {};
  const lines = fm.split('\n');
  let currentKey = null;
  let currentArray = null;

  for (const line of lines) {
    if (line.startsWith('  - ')) {
      // Array item
      if (currentArray !== null) {
        currentArray.push(line.slice(4).trim());
      }
      continue;
    }
    const match = line.match(/^(\w+):\s*(.*)$/);
    if (match) {
      const key = match[1];
      let value = match[2];
      // Strip quotes
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
      }
      if (value === '') {
        // Could be start of array
        currentKey = key;
        currentArray = [];
        result[key] = currentArray;
      } else {
        currentKey = key;
        currentArray = null;
        result[key] = value;
      }
    }
  }
  return result;
}

const files = process.argv.slice(2);
if (files.length === 0) {
  console.log('lint-frontmatter: no files to check');
  process.exit(0);
}

let hasErrors = false;

for (const file of files) {
  let raw;
  try {
    raw = readFileSync(file, 'utf8');
  } catch {
    console.error(`  ✗ Cannot read: ${file}`);
    hasErrors = true;
    continue;
  }

  const fmText = extractFrontmatter(raw);
  if (!fmText) {
    console.error(`  ✗ No frontmatter found: ${file}`);
    hasErrors = true;
    continue;
  }

  const fm = parseFrontmatter(fmText);
  const errors = [];

  for (const field of REQUIRED_FIELDS) {
    const value = fm[field.name];
    if (value === undefined || value === null) {
      errors.push(`missing required field: ${field.name}`);
    } else if (!field.test(value)) {
      if (field.name === 'description') {
        if (typeof value === 'string' && value.length < 50) {
          errors.push(`description too short (${value.length} chars, need 50-200)`);
        } else if (typeof value === 'string' && value.length > 200) {
          errors.push(`description too long (${value.length} chars, need 50-200)`);
        } else {
          errors.push(`invalid ${field.name}: expected ${field.type}`);
        }
      } else if (field.name === 'collection') {
        errors.push(`invalid collection: must be one of latest, highlights, data, mev, defi, math`);
      } else if (field.name === 'source_platform') {
        errors.push(`invalid source_platform: must be one of mirror, paragraph, github, ethresear.ch, frontier.tech`);
      } else if (field.name === 'slug') {
        errors.push(`invalid slug: must be lowercase letters, numbers, and hyphens only`);
      } else if (field.name === 'date') {
        errors.push(`invalid date: must be YYYY-MM-DD format`);
      } else if (field.name === 'tags') {
        errors.push(`invalid tags: must be an array containing 'writing'`);
      } else {
        errors.push(`invalid ${field.name}: expected ${field.type}`);
      }
    }
  }

  if (errors.length > 0) {
    console.error(`  ✗ ${file}`);
    for (const e of errors) {
      console.error(`    ${e}`);
    }
    hasErrors = true;
  } else {
    console.log(`  ✓ ${file}`);
  }
}

if (hasErrors) {
  process.exit(1);
} else {
  process.exit(0);
}
