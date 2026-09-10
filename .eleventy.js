const fs = require('fs');
const path = require('path');
const syntaxHighlight = require('@11ty/eleventy-plugin-syntaxhighlight');
const footnote = require('markdown-it-footnote');
module.exports = function(eleventyConfig) {
  eleventyConfig.addPlugin(syntaxHighlight);
  eleventyConfig.addPassthroughCopy('src/extras.css');
  eleventyConfig.addPassthroughCopy('src/extras.js');
  eleventyConfig.addPassthroughCopy('src/styles.css');
  eleventyConfig.addPassthroughCopy('src/assets');
  eleventyConfig.addPassthroughCopy('src/favicon.svg');
  eleventyConfig.addPassthroughCopy('src/robots.txt');
  eleventyConfig.addPassthroughCopy('src/search.js');
  eleventyConfig.addPassthroughCopy('src/site.js');
  eleventyConfig.addPassthroughCopy({ 'node_modules/katex/dist/katex.min.css': 'vendor/katex.min.css' });
  eleventyConfig.addPassthroughCopy({ 'node_modules/katex/dist/fonts': 'vendor/fonts' });

  // Markdown: KaTeX math ($...$ and $$...$$) rendered at build time.
  const markdownIt = require('markdown-it');
  const md = markdownIt({ html: true });
  try {
    const katexPlugin = require('@vscode/markdown-it-katex');
    md.use(katexPlugin.default || katexPlugin, { throwOnError: false });
  } catch (e) {
    console.warn('[eleventy] markdown-it-katex not available:', e.message);
  }
  md.use(footnote);
  eleventyConfig.setLibrary('md', md);

  // {% chart "assets/charts/foo.json", "Caption text" %}
  // Emits a lazy Plotly figure; site.js loads Plotly only when a chart is on the page.
  eleventyConfig.addShortcode('chart', (src, caption = '', opts = {}) => {
    const h = opts.height || 360;
    const cap = caption ? `<figcaption>${caption}</figcaption>` : '';
    return `<figure class="wide chart-figure"><div class="fig-box"><div class="chart" data-src="${src}" style="height:${h}px"></div></div>${cap}</figure>`;
  });

  // Group writings by year (newest first) for the archive.
  eleventyConfig.addFilter('byYear', (items) => {
    const groups = new Map();
    for (const it of items.slice().sort((a, b) => new Date(b.date) - new Date(a.date))) {
      const y = new Date(it.date).getFullYear();
      if (!groups.has(y)) groups.set(y, []);
      groups.get(y).push(it);
    }
    return [...groups.entries()].map(([year, writings]) => ({ year, writings }));
  });

  eleventyConfig.addFilter('shortDate', (date) => {
    if (!date) return '';
    const d = date instanceof Date ? date : new Date(String(date).split(' ')[0] + 'T00:00:00');
    return d.toLocaleDateString('en-US', { month: 'short' });
  });

  eleventyConfig.addCollection('writings', (collectionApi) => {
    return collectionApi.getFilteredByTag('writing');
  });

  // Build a collection of all topical tags (excluding structural tags like
  // 'writing' and collection/source-platform names) with their writings.
  // Returns an array of { name, slug, writings: [...] } sorted by writings count.
  const STRUCTURAL_TAGS = new Set([
    'writing', 'data', 'defi', 'highlights', 'latest', 'math', 'mev',
    'mirror', 'paragraph', 'github', 'ethresear.ch', 'frontier.tech',
  ]);
  eleventyConfig.addCollection('tagList', (collectionApi) => {
    const writings = collectionApi.getFilteredByTag('writing');
    const tagMap = new Map();
    for (const w of writings) {
      const tags = w.data.tags || [];
      for (const tag of tags) {
        if (STRUCTURAL_TAGS.has(tag)) continue;
        if (!tagMap.has(tag)) tagMap.set(tag, []);
        tagMap.get(tag).push(w);
      }
    }
    return [...tagMap.entries()]
      .map(([name, items]) => ({
        name,
        slug: slugify(name),
        writings: items.sort((a, b) => new Date(b.date) - new Date(a.date)),
      }))
      .sort((a, b) => b.writings.length - a.writings.length || a.name.localeCompare(b.name));
  });

  eleventyConfig.addFilter('formatDate', (date) => {
    if (!date) return '';
    let d;
    if (date instanceof Date) {
      d = date;
    } else if (String(date).includes('-')) {
      // Parse YYYY-MM-DD as local to avoid UTC timezone shift
      const [year, month, day] = String(date).split('-').map(Number);
      if (!year || !month || !day) return String(date);
      d = new Date(year, month - 1, day);
    } else {
      return String(date);
    }
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
  });

  eleventyConfig.addFilter('formatDateIso', (date) => {
    if (!date) return '';
    if (date instanceof Date) {
      return date.toISOString().split('T')[0];
    }
    if (String(date).includes('-')) {
      return String(date).split(' ')[0];
    }
    return String(date);
  });

  eleventyConfig.addFilter('sortByDate', (items) => {
    return items.slice().sort((a, b) => new Date(b.date) - new Date(a.date));
  });

  eleventyConfig.addFilter('groupByCollection', (items) => {
    const groups = {};
    for (const item of items) {
      const c = item.data.collection || 'uncategorized';
      if (!groups[c]) groups[c] = [];
      groups[c].push(item);
    }
    return groups;
  });

  eleventyConfig.addFilter('limit', (items, count) => {
    return items.slice(0, count);
  });

  eleventyConfig.addFilter('title', (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  });

  eleventyConfig.addFilter('absoluteUrl', (path) => {
    const base = 'https://Evan-Kim2028.github.io/evan_writings';
    const cleanPath = path && path.startsWith('/') ? path : '/' + (path || '');
    return base + cleanPath;
  });

  eleventyConfig.addFilter('striptags', (html) => {
    if (!html) return '';
    return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  });

  eleventyConfig.addFilter('join', (arr, sep) => {
    if (!Array.isArray(arr)) return '';
    return arr.join(sep || ', ');
  });

  eleventyConfig.addFilter('countByCollection', (items, collection) => {
    return items.filter(i => i.data.collection === collection).length;
  });

  eleventyConfig.addFilter('excerpt', (content) => {
    if (!content) return '';
    const text = content.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    const firstSentence = text.split(/\.\s+/)[0];
    return firstSentence.length > 180 ? firstSentence.slice(0, 180) + '…' : firstSentence + '.';
  });

  // Strip HTML tags and return plain text word count.
  eleventyConfig.addFilter('wordCount', (content) => {
    if (!content) return 0;
    const text = content.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    if (!text) return 0;
    return text.split(/\s+/).length;
  });

  // Reading time in minutes from rendered HTML content (200 wpm).
  // Returns a human label like "8 min read" or "1 min read".
  eleventyConfig.addFilter('readingTime', (content) => {
    const words = eleventyConfig.getFilter('wordCount')(content);
    if (!words) return '';
    const minutes = Math.max(1, Math.round(words / 200));
    return `${minutes} min read`;
  });

  // Extract the first <img src="..."> from rendered HTML content.
  // Returns the src path (root-relative, e.g. /evan_writings/assets/x.png)
  // or empty string if no image is present. The prefixAssets transform runs
  // AFTER templates render, so content here still has unprefixed /assets/
  // paths — we prepend the pathPrefix so absoluteImageUrl resolves correctly.
  const PATH_PREFIX = '/evan_writings';
  // Generated hero backdrop for posts without a hero image: a field of arrows
  // seeded from the slug, hue-shifted per post. Returns a CSS url() data URI.
  eleventyConfig.addFilter('heroPattern', (seed, theme) => {
    let h = 2166136261;
    for (const ch of String(seed || 'x')) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
    const rand = () => { h = (Math.imul(h, 1664525) + 1013904223) >>> 0; return h / 4294967296; };
    const hue = Math.floor(rand() * 360);
    const dark = theme === 'dark';
    const bg1 = dark ? `hsl(${hue} 30% 8%)` : `hsl(${hue} 35% 96%)`;
    const bg2 = dark ? `hsl(${(hue + 30) % 360} 32% 13%)` : `hsl(${(hue + 30) % 360} 30% 91%)`;
    const ink = dark ? `hsl(${hue} 30% 48%)` : `hsl(${hue} 30% 55%)`;
    const acc = dark ? `hsl(${(hue + 150) % 360} 60% 60%)` : `hsl(${(hue + 150) % 360} 55% 40%)`;
    const ang = (12 + rand() * 20) * Math.PI / 180;
    let lines = '';
    for (let x = -20; x < 1620; x += 52) for (let y = -20; y < 620; y += 52) {
      const jx = x + (rand() - .5) * 18, jy = y + (rand() - .5) * 18, L = 26;
      const op = (0.35 + rand() * 0.5).toFixed(2);
      lines += `<line x1="${jx.toFixed(0)}" y1="${jy.toFixed(0)}" x2="${(jx + L * Math.cos(ang)).toFixed(0)}" y2="${(jy + L * Math.sin(ang)).toFixed(0)}" stroke="${ink}" stroke-width="1.4" opacity="${op}" marker-end="url(#m)"/>`;
    }
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="600" viewBox="0 0 1600 600"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${bg1}"/><stop offset="1" stop-color="${bg2}"/></linearGradient><marker id="m" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6z" fill="${ink}"/></marker></defs><rect width="1600" height="600" fill="url(#g)"/>${lines}<line x1="1240" y1="470" x2="1340" y2="250" stroke="${acc}" stroke-width="4" stroke-linecap="round"/></svg>`;
    return `url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`;
  });

  eleventyConfig.addFilter('firstImage', (content) => {
    if (!content) return '';
    const m = String(content).match(/<img[^>]+src="([^"]+)"/i);
    if (!m) return '';
    let src = m[1];
    if (/^https?:\/\//.test(src) || src.startsWith('data:')) return src;
    // Normalize unprefixed /assets/ -> /evan_writings/assets/
    if (src.startsWith('/assets/')) src = PATH_PREFIX + src;
    return src;
  });

  // Resolve a root-relative image path to an absolute URL (for OG/Twitter).
  eleventyConfig.addFilter('absoluteImageUrl', (src) => {
    if (!src) return '';
    if (/^https?:\/\//.test(src)) return src;
    const base = 'https://Evan-Kim2028.github.io';
    const p = src.startsWith('/') ? src : '/' + src;
    return base + p;
  });

  // ISO 8601 date for JSON-LD / article:published_time.
  eleventyConfig.addFilter('isoDate', (date) => {
    if (!date) return '';
    let d;
    if (date instanceof Date) {
      d = date;
    } else if (String(date).includes('-')) {
      const [year, month, day] = String(date).split('-').map(Number);
      if (!year || !month || !day) return '';
      d = new Date(year, month - 1, day);
    } else {
      return '';
    }
    return d.toISOString().split('T')[0];
  });

  // ISO date or now — for Atom feed <updated> when a collection item is passed.
  eleventyConfig.addFilter('isoDateOrNow', (item) => {
    const date = item && item.data ? item.data.date : item;
    const iso = eleventyConfig.getFilter('isoDate')(date);
    return iso || new Date().toISOString();
  });

  // Escape a string for safe inclusion in JSON-LD <script> output.
  eleventyConfig.addFilter('jsonLdEscape', (str) => {
    if (str == null) return '';
    return String(str)
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .replace(/\t/g, '\\t');
  });

  // JSON.stringify wrapper for use inside Nunjucks templates.
  eleventyConfig.addFilter('jsonify', (value) => {
    return JSON.stringify(value == null ? '' : value);
  });

  // Filter out structural tags (writing, collection, source platform) from a
  // tags array, returning only the meaningful topical tags for SEO.
  eleventyConfig.addFilter('seoTags', (tags, collection) => {
    if (!Array.isArray(tags)) return [];
    return tags.filter((t) => !STRUCTURAL_TAGS.has(t) && t !== collection);
  });

  // Slugify a tag name for use in tag page URLs.
  eleventyConfig.addFilter('tagSlug', (tag) => slugify(tag));

  // Pluralize: returns 's' for counts != 1, '' for count == 1.
  eleventyConfig.addFilter('pluralize', (count) => (count === 1 ? '' : 's'));

  // Check if a tag is topical (not structural).
  eleventyConfig.addFilter('isTopicalTag', (tag) => !STRUCTURAL_TAGS.has(tag));

  // Related writings: same collection, excluding the current page, newest first.
  eleventyConfig.addFilter('related', (writings, currentPage, collection, limit = 3) => {
    if (!Array.isArray(writings)) return [];
    return writings
      .filter((w) => w.data.collection === collection && w.url !== currentPage.url)
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, limit);
  });

  // Slugify a heading text into a URL-safe anchor id.
  function slugify(text) {
    return String(text)
      .toLowerCase()
      .replace(/<[^>]+>/g, '')
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  // Build a table-of-contents nav from the H2/H3 headings in rendered HTML.
  // Returns an HTML string (empty if fewer than 2 headings).
  eleventyConfig.addFilter('toc', (content) => {
    if (!content) return '';
    const headingRe = /<h([23])[^>]*>([\s\S]*?)<\/h\1>/gi;
    const items = [];
    let m;
    while ((m = headingRe.exec(content)) !== null) {
      const level = parseInt(m[1], 10);
      const text = m[2].replace(/<[^>]+>/g, '').trim();
      if (!text) continue;
      const id = slugify(text);
      items.push({ level, text, id });
    }
    if (items.length < 2) return '';
    const links = items.map((it) => {
      const cls = it.level === 2 ? 'toc-link toc-link-h2' : 'toc-link toc-link-h3';
      return `<a href="#${it.id}" class="${cls}">${it.text}</a>`;
    }).join('\n');
    return `<nav class="toc" aria-label="Table of contents"><p class="toc-title">On this page</p>${links}</nav>`;
  });

  // Rewrite markdown asset paths to include the repo path prefix
  eleventyConfig.addTransform('prefixAssets', (content, outputPath) => {
    if (outputPath && outputPath.endsWith('.html')) {
      let out = content
        .replace(/src="\/assets\//g, 'src="/evan_writings/assets/')
        .replace(/href="\/assets\//g, 'href="/evan_writings/assets/');
      // Inject id attributes on H2/H3 inside .writing-body so TOC anchors resolve.
      // Only adds an id when the heading doesn't already have one.
      out = out.replace(/(<h([23]))((?:(?!id=)[^>])*)(>[\s\S]*?<\/h\2>)/gi, (match, open, level, attrs, rest) => {
        if (/\bid=/i.test(attrs)) return match;
        const text = rest.replace(/<[^>]+>/g, '').replace(/<\/?h[23]>/gi, '').trim();
        const id = slugify(text);
        if (!id) return match;
        const inner = rest.replace(/^>/, '').replace(new RegExp(`</h${level}>$`, 'i'), '');
        return `${open}${attrs} id="${id}"><a class="h-link" href="#${id}">${inner}</a></h${level}>`;
      });
      // Wrap standalone images into <figure>; an immediately following
      // paragraph that is only <em>…</em> becomes the figcaption.
      out = out.replace(/<p>(<img[^>]+>)<\/p>\s*(?:<p><em>([\s\S]*?)<\/em><\/p>)?/gi, (m, img, cap) => {
        const c = cap ? `<figcaption>${cap}</figcaption>` : '';
        // If a `.dark.<ext>` sibling exists under src/assets, emit a light/dark pair
        // toggled by [data-theme] (see .img-light/.img-dark in styles.css).
        const sm = img.match(/src="\/evan_writings(\/assets\/[^"]+)\.(png|jpg|jpeg|webp|svg)"/i);
        if (sm) {
          const darkRel = `${sm[1]}.dark.${sm[2]}`;
          if (fs.existsSync(path.join(__dirname, 'src', darkRel))) {
            const light = img.replace(/<img/i, '<img class="img-light"');
            const dark = img.replace(/<img/i, '<img class="img-dark"').replace(sm[0], `src="/evan_writings${darkRel}"`);
            return `<figure class="wide">${light}${dark}${c}</figure>`;
          }
        }
        return `<figure class="wide">${img}${c}</figure>`;
      });
      // Wrap markdown tables so they can break out of the prose column and sort.
      out = out.replace(/<table>([\s\S]*?)<\/table>/gi, (m) =>
        `<figure class="wide"><div class="fig-box table-wrap">${m.replace('<table>', '<table class="sortable">')}</div></figure>`);
      return out;
    }
    return content;
  });

  return {
    dir: {
      input: 'src',
      output: '_site',
      includes: '_includes',
      data: '_data'
    },
    pathPrefix: '/evan_writings/',
    templateFormats: ['md', 'njk', 'txt']
  };
};
