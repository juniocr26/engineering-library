import { readFile } from 'node:fs/promises';
import path from 'node:path';

// Fixed bundled script. Docker installs dependencies above the source mount.
export async function GET() {
  let directory = process.cwd();
  while (true) {
    try {
      const script = await readFile(path.join(directory, 'node_modules/mermaid/dist/mermaid.min.js'));
      return new Response(script, { headers: { 'Content-Type': 'application/javascript', 'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'public, max-age=3600', 'Access-Control-Allow-Origin': '*' } });
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
      const parent = path.dirname(directory);
      if (parent === directory) throw error;
      directory = parent;
    }
  }
}
