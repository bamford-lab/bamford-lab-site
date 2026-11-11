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
  eleventyConfig.addFilter("limit", (arr, n) => arr.slice(0, n));

  // Render a frontmatter string as markdown (used by profile-page sections)
  const md = require("markdown-it")({ html: true, linkify: true, typographer: false });
  eleventyConfig.addFilter("markdown", (s) => (s ? md.render(s) : ""));
  eleventyConfig.addFilter("monthYear", (d) =>
    new Date(d).toLocaleString("en-GB", { month: "long", year: "numeric" })
  );

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
