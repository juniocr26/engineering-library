import { readFile } from 'node:fs/promises';
import path from 'node:path';

// A fixed bundled script, never a user-controlled URL or filesystem path.
export async function GET() {
  const script = await readFile(path.join(process.cwd(), 'node_modules/mermaid/dist/mermaid.min.js'));
  return new Response(script, { headers: { 'Content-Type': 'application/javascript', 'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'public, max-age=3600', 'Access-Control-Allow-Origin': '*' } });
}
