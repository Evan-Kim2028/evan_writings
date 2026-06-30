module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy('src/styles.css');
  eleventyConfig.addPassthroughCopy('src/assets');

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

  // Rewrite markdown asset paths to include the repo path prefix
  eleventyConfig.addTransform('prefixAssets', (content, outputPath) => {
    if (outputPath && outputPath.endsWith('.html')) {
      return content
        .replace(/src="\/assets\//g, 'src="/evan_writings/assets/')
        .replace(/href="\/assets\//g, 'href="/evan_writings/assets/');
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
