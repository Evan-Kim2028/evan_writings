#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { rankWritings } from './search.js';
import type { Writing } from './types.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

function findLlmsFullTxt(): string {
  // Try several locations relative to the MCP server
  const candidates = [
    join(__dirname, '..', '..', '_site', 'llms-full.txt'),
    join(__dirname, '..', '..', 'src', 'llms-full.txt.njk'),
    join(process.cwd(), '_site', 'llms-full.txt'),
    join(process.cwd(), 'llms-full.txt'),
  ];
  for (const path of candidates) {
    try {
      readFileSync(path, 'utf-8');
      return path;
    } catch {
      // continue
    }
  }
  return candidates[0];
}

function parseWritings(content: string): Writing[] {
  const writings: Writing[] = [];
  const entries = content.split(/^---\s*$/m);
  for (const entry of entries) {
    const lines = entry.split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length === 0) continue;

    const title = lines[0].replace(/^##\s*/, '');
    const meta: Record<string, string> = {};
    let bodyStart = -1;
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('- ')) {
        const m = line.match(/^-\s*(\w+):\s*(.+)$/);
        if (m) {
          meta[m[1].toLowerCase()] = m[2];
        }
      } else {
        bodyStart = i;
        break;
      }
    }
    const body = bodyStart >= 0 ? lines.slice(bodyStart).join('\n') : '';
    writings.push({
      title,
      date: meta.date || '',
      collection: meta.collection || '',
      tags: meta.tags ? meta.tags.split(',').map(t => t.trim()) : [],
      url: meta.url || '',
      original: meta.original || '',
      body,
    });
  }
  return writings;
}

function loadWritings(): Writing[] {
  const path = findLlmsFullTxt();
  const content = readFileSync(path, 'utf-8');
  return parseWritings(content);
}

const writings = loadWritings();

const server = new Server(
  {
    name: 'evan-writings-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'list_writings',
        description: 'List all writings with metadata. Optionally filter by collection.',
        inputSchema: {
          type: 'object',
          properties: {
            collection: {
              type: 'string',
              description: 'Filter by collection (latest, highlights, data, mev, defi, math)',
            },
          },
        },
      },
      {
        name: 'search_writings',
        description: 'Search writings by keyword or phrase. Returns ranked matches.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query',
            },
            count: {
              type: 'number',
              description: 'Maximum number of results',
              default: 10,
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'get_writing',
        description: 'Get the full content of a writing by title.',
        inputSchema: {
          type: 'object',
          properties: {
            title: {
              type: 'string',
              description: 'Exact or partial title of the writing',
            },
          },
          required: ['title'],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'list_writings') {
    const collection = (args?.collection as string) || '';
    const filtered = collection
      ? writings.filter(w => w.collection.toLowerCase() === collection.toLowerCase())
      : writings;
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(filtered.map(w => ({
            title: w.title,
            date: w.date,
            collection: w.collection,
            tags: w.tags,
            url: w.url,
            original: w.original,
          })), null, 2),
        },
      ],
    };
  }

  if (name === 'search_writings') {
    const query = (args?.query as string) || '';
    const count = (args?.count as number) || 10;
    const results = rankWritings(query, writings).slice(0, count);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(results.map(r => ({
            title: r.writing.title,
            date: r.writing.date,
            collection: r.writing.collection,
            url: r.writing.url,
            original: r.writing.original,
            score: r.score,
          })), null, 2),
        },
      ],
    };
  }

  if (name === 'get_writing') {
    const title = (args?.title as string) || '';
    const matches = writings.filter(w =>
      w.title.toLowerCase().includes(title.toLowerCase())
    );
    if (matches.length === 0) {
      return {
        content: [
          {
            type: 'text',
            text: `No writing found matching "${title}".`,
          },
        ],
        isError: true,
      };
    }
    const writing = matches[0];
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            title: writing.title,
            date: writing.date,
            collection: writing.collection,
            tags: writing.tags,
            url: writing.url,
            original: writing.original,
            body: writing.body,
          }, null, 2),
        },
      ],
    };
  }

  return {
    content: [{ type: 'text', text: `Unknown tool: ${name}` }],
    isError: true,
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
