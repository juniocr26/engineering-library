import { createRequire } from 'node:module';
import path from 'node:path';
const require = createRequire(import.meta.url);

const config = {
  // Container dependencies live one directory above the mounted frontend.
  outputFileTracingRoot: path.resolve(import.meta.dirname, '..'),
  webpack(config) {
    // Markdown's browser entity decoder requires document. Use its equivalent
    // DOM-free implementation so the same parser can run in a Web Worker.
    config.resolve.alias['decode-named-character-reference'] = require.resolve('decode-named-character-reference');
    return config;
  },
};

export default config;
