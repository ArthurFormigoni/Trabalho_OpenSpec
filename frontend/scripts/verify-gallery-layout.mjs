import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const app = await readFile(new URL("../src/App.tsx", import.meta.url), "utf8");
const styles = await readFile(new URL("../src/styles.css", import.meta.url), "utf8");

assert.doesNotMatch(app, /style=\{\{\s*aspectRatio:/, "gallery cards must not use variable frame ratios");
assert.match(styles, /aspect-ratio:\s*1\s*\/\s*1/, "gallery cards must use a uniform square frame");
assert.match(styles, /object-fit: fill/, "gallery images must fill the complete square");
assert.match(styles, /width: 100%/, "gallery images must fill the card width");
assert.match(styles, /height: 100%/, "gallery images must fill the card height");
assert.doesNotMatch(styles, /object-fit:\s*cover/, "gallery must not crop images");
assert.match(styles, /grid-template-columns:\s*repeat\(3,/, "desktop gallery must have at most three columns");

console.log("Gallery layout verification passed: full square fill, no crop, and no four-column grid detected.");
