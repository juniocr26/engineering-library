import { realpath, readFile } from 'node:fs/promises';
import path from 'node:path';
const types: Record<string, string> = { svg: 'image/svg+xml', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp', gif: 'image/gif' };
export async function GET(_request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const parts = (await params).path;
  if (parts.some(part => !part || part === '.' || part === '..' || /[\\\0/]/.test(part))) return new Response(null, { status: 404 });
  const mime = types[parts.at(-1)?.split('.').at(-1)?.toLowerCase() ?? ''];
  if (!mime) return new Response(null, { status: 404 });
  try {
    const root = await realpath(path.resolve(process.env.DOCUMENTATION_ROOT ?? path.resolve(process.cwd(), '../docs/projects'), '../img'));
    const file = await realpath(path.join(root, ...parts));
    if (!file.startsWith(root + path.sep)) return new Response(null, { status: 404 });
    return new Response(new Uint8Array(await readFile(file)), { headers: { 'Content-Type': mime, 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'none'; sandbox", 'Cache-Control': 'public, max-age=300' } });
  } catch { return new Response(null, { status: 404 }); }
}
