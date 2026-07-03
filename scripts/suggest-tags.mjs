#!/usr/bin/env node
// Tag suggestion script for evan_writings.
//
// Analyzes each writing's title, description, and content to suggest
// topical tags from a controlled vocabulary. Outputs a JSON report
// for human review before writing tags into frontmatter.
//
// Usage:
//   node scripts/suggest-tags.mjs           # print suggestions to stdout
//   node scripts/suggest-tags.mjs --write   # write approved tags into frontmatter
//
// The controlled vocabulary maps canonical tag names to keyword patterns.
// A writing gets a tag if any of its keywords appear in the title (weight 3),
// description (weight 2), or content body (weight 1, with frequency threshold).

import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const WRITINGS_DIR = join(ROOT, 'src', 'writings');

// ---------- Controlled vocabulary ----------
// Each entry: [canonicalTag, [keywordPatterns]]
// Keywords are matched case-insensitively as whole words (boundaries).
// Keep tags lowercase, hyphenated, SEO-friendly.
const VOCABULARY = [
  // Blockchain ecosystems
  ['ethereum', ['ethereum', 'eth ', 'ether', 'eip-4844', 'eip4844']],
  ['solana', ['solana', 'helius', 'jito', 'solanapy']],
  ['sui', ['sui ', 'sui\n', 'sui.', 'move language', 'sui blockchain']],
  ['polygon', ['polygon', 'matic']],
  ['optimism', ['optimism', 'op stack', 'optimism stack']],

  // Protocols & platforms
  ['uniswap', ['uniswap', 'uni v2', 'uni v3', 'uniswap v2', 'uniswap v3']],
  ['olympus', ['olympus', 'ohm', 'rebase token', '(3,3)']],
  ['balancer', ['balancer', 'managed pool', 'boosted pool']],
  ['beanstalk', ['beanstalk', 'bean ', 'credit-based stablecoin']],
  ['ust', ['ust ', 'terra', 'luna', 'anchor protocol']],
  ['courtyard', ['courtyard']],
  ['opensea', ['opensea', 'seaport']],
  ['sudo', ['sudo', 'sudoswap']],

  // DeFi mechanisms
  ['amm', ['amm', 'automated market maker', 'cpmm', 'cfmm', 'rmm', 'concentrated liquidity', 'liquidity pool']],
  ['stablecoin', ['stablecoin', 'stable coin', 'peg', 'seigniorage']],
  ['liquidity', ['liquidity', 'lp ', 'lping', 'liquidity provision', 'liquidity management']],
  ['bonding-curve', ['bonding curve', 'bonding curves', 'token curve']],
  ['market-maker', ['market maker', 'market makers', 'replicating market maker', 'rmm-01']],
  ['pari-mutuel', ['pari-mutuel', 'pari mutuel', 'lmsr', 'hanson']],
  ['nft', ['nft', 'nfts', 'non-fungible', 'digital collectible', 'rootlets']],

  // MEV & trading
  ['mev', ['mev', 'maximal extractable value', 'arbitrage', 'sandwich', 'frontrunning', 'front-running', 'reordering']],
  ['blob-market', ['blob', 'blobs', 'blob market', 'eip-4844', 'proto-danksharding', 'blob fee', 'blob inclusion']],
  ['preconfirmations', ['preconfirmation', 'preconfirmations', 'preconf', 'mev-commit', 'primev']],
  ['slot-inclusion', ['slot inclusion', 'inclusion rate', 'inclusion delay', 'block inclusion']],
  ['jito-tips', ['jito', 'tip', 'tips', 'priority fee', 'compute cost']],

  // Data & infrastructure
  ['iceberg', ['iceberg', 'lakehouse', 'apache iceberg', 'pyiceberg']],
  ['duckdb', ['duckdb']],
  ['lancedb', ['lancedb', 'lance db']],
  ['data-pipeline', ['pipeline', 'etl', 'data pipeline', 'data ingestion', 'streaming pipeline']],
  ['subgraph', ['the graph', 'subgrounds', 'datastreams', 'subgraph query', 'graph protocol']],
  ['sentio', ['sentio', 'sentio pipelines']],
  ['mcp', ['mcp', 'model context protocol', 'agentic', 'agentic-native']],
  ['dune', ['dune', 'dune.com', 'dune analytics']],
  ['flipside', ['flipside', 'flipside crypto']],
  ['cryo', ['cryo', 'merkle', 'reth', 'archive node']],
  ['olap', ['olap', 'online analytical processing', 'columnar storage', 'parquet']],
  ['data-observability', ['observability', 'monitoring', 'data observability']],

  // Math
  ['measure-theory', ['measure theory', 'lebesgue', 'sigma-algebra', 'measurable function', 'integration']],
  ['abstract-algebra', ['abstract algebra', 'group theory', 'kernel', 'normal subgroup', 'homomorphism', 'quotient group']],
  ['groebner-basis', ['groebner', 'gröbner', 'polynomial ideal', 'geometric theorem', 'mathematica']],
  ['neural-networks', ['perceptron', 'neural network', 'activation function', 'binary classification', 'learning rule']],
  ['quadratic-reciprocity', ['quadratic reciprocity', 'lucas polynomial', 'lucas sequence', 'number theory']],
  ['gaussian-math', ['gaussian', 'normal cdf', 'rational approximation', 'horner', 'fixed-point arithmetic']],
  ['topological-data-analysis', ['topological data analysis', 'tda', 'mapper algorithm', 'persistent homology', 'clustering']],
  ['graph-theory', ['graph theory', 'complete graph', 'dao structure', 'decentralization metric']],

  // Analytics methods
  ['clustering', ['clustering', 'agglomerative', 'k-means', 'unsupervised']],
  ['kernel-density', ['kernel density', 'kde', 'density estimation']],
  ['quantitative-modeling', ['quantitative', 'quantitative model', 'momentum strategy', 'crossover', 'backtesting']],
  ['control-theory', ['control theory', 'optimization model', 'feedback control', 'pid controller']],

  // Oracle & execution
  ['oracle', ['oracle', 'price oracle', 'pyth', 'chainlink', 'low-latency']],
  ['atomic-execution', ['atomic arbitrage', 'atomic execution', 'flashbots', 'bundle', 'atomic swap']],

  // DAO & governance
  ['dao', ['dao', 'governance', 'decentralized autonomous']],
];

// Tags to never suggest (already in frontmatter as collection/source)
const SKIP_TAGS = new Set([
  'writing', 'data', 'defi', 'highlights', 'latest', 'math', 'mev',
  'mirror', 'paragraph', 'github', 'ethresear.ch', 'frontier.tech',
]);

// ---------- Tag extraction logic ----------

function extractFrontmatter(raw) {
  if (!raw.startsWith('---')) return { fm: '', body: raw, end: -1 };
  const end = raw.indexOf('\n---', 3);
  if (end === -1) return { fm: '', body: raw, end: -1 };
  return { fm: raw.slice(3, end), body: raw.slice(end + 4), end };
}

function parseExistingTags(fm) {
  const tagsMatch = fm.match(/^tags:\s*\n((?:  - .+\n)+)/m);
  if (!tagsMatch) return [];
  return tagsMatch[1]
    .split('\n')
    .map((l) => l.replace(/^  - /, '').trim())
    .filter(Boolean);
}

function countOccurrences(haystack, pattern) {
  const re = new RegExp(`\\b${pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
  return (haystack.match(re) || []).length;
}

function suggestTags(title, description, body) {
  const suggestions = [];
  const titleLower = title.toLowerCase();
  const descLower = (description || '').toLowerCase();
  const bodyLower = body.toLowerCase();
  // Limit body search to first 5000 chars to avoid huge content skewing
  const bodySample = bodyLower.slice(0, 8000);

  for (const [tag, keywords] of VOCABULARY) {
    if (SKIP_TAGS.has(tag)) continue;

    let score = 0;
    let hits = [];

    for (const kw of keywords) {
      const tCount = countOccurrences(titleLower, kw);
      const dCount = countOccurrences(descLower, kw);
      const bCount = countOccurrences(bodySample, kw);

      if (tCount > 0) { score += tCount * 3; hits.push(`title(${tCount})`); }
      if (dCount > 0) { score += dCount * 2; hits.push(`desc(${dCount})`); }
      if (bCount >= 2) { score += bCount; hits.push(`body(${bCount})`); }
      // Single body mention with title/desc hit is also ok
      if (bCount === 1 && (tCount > 0 || dCount > 0)) { score += 1; hits.push(`body(1)`); }
    }

    if (score >= 3) {
      suggestions.push({ tag, score, hits: hits.join(', ') });
    }
  }

  return suggestions.sort((a, b) => b.score - a.score);
}

// ---------- Main ----------

const writeMode = process.argv.includes('--write');
const mdFiles = readdirSync(WRITINGS_DIR)
  .filter((f) => f.endsWith('.md'))
  .map((f) => join(WRITINGS_DIR, f));

const report = {};
let totalNewTags = 0;

for (const mdFile of mdFiles) {
  const raw = readFileSync(mdFile, 'utf8');
  const { fm, body } = extractFrontmatter(raw);

  // Extract title and description from frontmatter
  const titleMatch = fm.match(/^title:\s+"?(.+?)"?\s*$/m);
  const descMatch = fm.match(/^description:\s+"?(.+?)"?\s*$/m);
  const title = titleMatch ? titleMatch[1] : basename(mdFile, '.md');
  const description = descMatch ? descMatch[1] : '';

  const existingTags = parseExistingTags(fm);
  const suggestions = suggestTags(title, description, body);

  // Filter out tags already present
  const newTags = suggestions.filter((s) => !existingTags.includes(s.tag));
  const confirmedTags = newTags.map((s) => s.tag);

  if (confirmedTags.length > 0) {
    totalNewTags += confirmedTags.length;
    report[basename(mdFile)] = {
      title,
      existingTags,
      suggestedTags: confirmedTags,
      details: newTags.map((s) => `${s.tag} (score=${s.score}, ${s.hits})`),
    };
  }
}

// Output report
console.log(`\nTag Suggestion Report`);
console.log(`${'='.repeat(60)}`);
console.log(`Writings analyzed: ${mdFiles.length}`);
console.log(`Writings with new tag suggestions: ${Object.keys(report).length}`);
console.log(`Total new tags suggested: ${totalNewTags}`);
console.log(`${'='.repeat(60)}\n`);

for (const [filename, data] of Object.entries(report)) {
  console.log(`📄 ${filename}`);
  console.log(`   Title: ${data.title}`);
  console.log(`   Existing tags: [${data.existingTags.join(', ')}]`);
  console.log(`   Suggested new tags: [${data.suggestedTags.join(', ')}]`);
  for (const detail of data.details) {
    console.log(`     → ${detail}`);
  }
  console.log();
}

// Tag frequency summary
const tagFreq = {};
for (const data of Object.values(report)) {
  for (const tag of data.suggestedTags) {
    tagFreq[tag] = (tagFreq[tag] || 0) + 1;
  }
}
console.log(`\nTag frequency (suggested):`);
const sorted = Object.entries(tagFreq).sort((a, b) => b[1] - a[1]);
for (const [tag, count] of sorted) {
  console.log(`  ${tag}: ${count} writings`);
}

if (writeMode) {
  console.log(`\n${'='.repeat(60)}`);
  console.log('Writing tags into frontmatter...');
  for (const mdFile of mdFiles) {
    const filename = basename(mdFile);
    if (!report[filename]) continue;

    const raw = readFileSync(mdFile, 'utf8');
    const { fm, body, end } = extractFrontmatter(raw);
    if (end === -1) continue;

    const existingTags = parseExistingTags(fm);
    const newTags = report[filename].suggestedTags.filter((t) => !existingTags.includes(t));
    if (newTags.length === 0) continue;

    const allTags = [...existingTags, ...newTags];
    const tagsBlock = `tags:\n${allTags.map((t) => `  - ${t}`).join('\n')}\n`;

    // Replace existing tags block or add before closing ---
    let newFm;
    const tagsMatch = fm.match(/^tags:\s*\n((?:  - .+\n)+)/m);
    if (tagsMatch) {
      newFm = fm.replace(tagsMatch[0], tagsBlock);
    } else {
      newFm = fm.trimEnd() + '\n' + tagsBlock;
    }

    const newRaw = '---' + newFm + '---' + body;
    writeFileSync(mdFile, newRaw);
    console.log(`  ✓ ${filename}: +${newTags.length} tags`);
  }
  console.log('Done.');
} else {
  console.log(`\n${'='.repeat(60)}`);
  console.log('Dry run — no files modified.');
  console.log('Run with --write to apply tags to frontmatter.');
}
