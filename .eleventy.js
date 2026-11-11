module.exports = function (eleventyConfig) {
  // Copy static assets and the CMS admin straight through
  eleventyConfig.addPassthroughCopy("src/assets");
  eleventyConfig.addPassthroughCopy("src/admin");

  // Current members, sorted by "order". Drafts and alumni are excluded.
  eleventyConfig.addCollection("people", (c) =>
    c.getFilteredByGlob("src/people/*.md")
      .filter((p) => !p.data.draft && !p.data.alumni)
      .sort((a, b) => (a.data.order || 99) - (b.data.order || 99))
  );

  // Past members. Listed on /people/ but given no profile page of their own.
  eleventyConfig.addCollection("alumni", (c) =>
    c.getFilteredByGlob("src/people/*.md")
      .filter((p) => !p.data.draft && p.data.alumni)
      .sort((a, b) => (a.data.order || 99) - (b.data.order || 99))
  );

  // News, newest first
  eleventyConfig.addCollection("news", (c) =>
    c.getFilteredByGlob("src/news/*.md")
      .filter((p) => !p.data.draft)
      .sort((a, b) => new Date(b.data.date) - new Date(a.data.date))
  );

  // Helpers
  // Appends a content hash to an asset URL, so a changed photo is never served from
  // a browser's cache under its old filename. Bitten twice on 11 Nov 2026: an updated
  // stylesheet and then an updated headshot both looked unchanged until a hard refresh.
  const { createHash } = require("node:crypto");
  const { readFileSync, existsSync } = require("node:fs");
  const { join } = require("node:path");
  const bustCache = new Map();
  eleventyConfig.addFilter("bust", (url) => {
    if (!url || !url.startsWith("/")) return url;
    if (bustCache.has(url)) return bustCache.get(url);
    const file = join(__dirname, "src", url);
    let out = url;
    if (existsSync(file)) {
      const h = createHash("sha1").update(readFileSync(file)).digest("hex").slice(0, 8);
      out = `${url}?v=${h}`;
    }
    bustCache.set(url, out);
    return out;
  });

  eleventyConfig.addFilter("limit", (arr, n) => arr.slice(0, n));

  // Render a frontmatter string as markdown (used by profile-page sections)
  const md = require("markdown-it")({ html: true, linkify: true, typographer: false });
  eleventyConfig.addFilter("markdown", (s) => (s ? md.render(s) : ""));
  eleventyConfig.addFilter("isoDate", (d) => new Date(d).toISOString().slice(0, 10));
  eleventyConfig.addFilter("monthYear", (d) =>
    new Date(d).toLocaleString("en-GB", { month: "long", year: "numeric" })
  );

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
