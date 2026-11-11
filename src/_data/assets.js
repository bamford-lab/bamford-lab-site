// Fingerprints the stylesheet so the browser can never serve a cached styles.css
// against freshly deployed HTML. That mismatch renders the page unstyled: it happened
// on 11 Nov 2026 when new markup landed while the old CSS was still cached.
// The hash changes only when the file changes, so caching still works between deploys.
const { createHash } = require("node:crypto");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");

const hash = (file) =>
  createHash("sha1").update(readFileSync(join(__dirname, "..", file))).digest("hex").slice(0, 8);

module.exports = () => ({ cssVersion: hash("assets/styles.css") });
