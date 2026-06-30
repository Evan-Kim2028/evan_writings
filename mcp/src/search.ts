import type { Writing, SearchResult } from './types.js';

function tokenize(text: string): string[] {
  return text.toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2);
}

function termFrequency(term: string, tokens: string[]): number {
  return tokens.filter(t => t === term).length;
}

function inverseDocumentFrequency(term: string, docs: string[][]): number {
  const containing = docs.filter(tokens => tokens.includes(term)).length;
  if (containing === 0) return 0;
  return Math.log(docs.length / containing);
}

export function rankWritings(query: string, writings: Writing[]): SearchResult[] {
  const queryTokens = tokenize(query);
  if (queryTokens.length === 0) {
    return writings.map(w => ({ writing: w, score: 0 }));
  }

  const docTokens = writings.map(w => tokenize(`${w.title} ${w.body} ${w.tags.join(' ')}`));
  const scores: SearchResult[] = [];

  for (let i = 0; i < writings.length; i++) {
    const writing = writings[i];
    let score = 0;
    for (const term of queryTokens) {
      const tf = termFrequency(term, docTokens[i]);
      const idf = inverseDocumentFrequency(term, docTokens);
      // Boost title matches
      const titleTokens = tokenize(writing.title);
      const titleBoost = titleTokens.includes(term) ? 3 : 1;
      score += tf * idf * titleBoost;
    }
    scores.push({ writing, score });
  }

  return scores
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score);
}
