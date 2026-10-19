import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);

const config = {
  webpack(config) {
    // Markdown's browser entity decoder requires document. Use its equivalent
    // DOM-free implementation so the same parser can run in a Web Worker.
    config.resolve.alias['decode-named-character-reference'] = require.resolve('decode-named-character-reference');
    return config;
  },
};

export default config;
