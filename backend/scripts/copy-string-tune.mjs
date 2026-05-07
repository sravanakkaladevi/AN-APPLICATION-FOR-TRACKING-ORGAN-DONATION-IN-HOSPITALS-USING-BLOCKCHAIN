import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";

const source = resolve("node_modules/@fiddle-digital/string-tune/dist/index.mjs");
const target = resolve("core/static/core/vendor/string-tune/index.mjs");

mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);
