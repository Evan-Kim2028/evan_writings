module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy('src/styles.css');
  eleventyConfig.addPassthroughCopy('src/assets');
  eleventyConfig.addPassthroughCopy('src/favicon.svg');
  eleventyConfig.addPassthroughCopy('src/robots.txt');

  eleventyConfig.addCollection('writings', (collectionApi) => {
    return collectionApi.getFilteredByTag('writing');
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

  // Filter out the generic 'writing' tag and the collection name from a tags
  // array, returning only the meaningful tags for SEO.
  eleventyConfig.addFilter('seoTags', (tags, collection) => {
    if (!Array.isArray(tags)) return [];
    return tags.filter((t) => t !== 'writing' && t !== collection);
  });

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
        return `${open}${attrs} id="${id}"${rest}`;
      });
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
