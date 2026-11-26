import { validProjectDirectory } from '../../../../lib/catalog-paths.ts';
import { realpath, readFile } from 'node:fs/promises';
import path from 'node:path';
const documentationRoot = () => process.env.DOCUMENTATION_ROOT ?? path.resolve(process.cwd(), '../docs');
const types: Record<string, string> = { svg: 'image/svg+xml', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp', gif: 'image/gif' };
export async function GET(_request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const parts = (await params).path;
  if (parts.some(part => !part || part === '.' || part === '..' || /[\\\0/]/.test(part))) return new Response(null, { status: 404 });
  const mime = types[parts.at(-1)?.split('.').at(-1)?.toLowerCase() ?? ''];
  if (!mime) return new Response(null, { status: 404 });
  try {
    if (!validProjectDirectory(parts[0]) || !(parts[1] === 'img' || (['en', 'pt-br'].includes(parts[1]) && parts[2] === 'img'))) return new Response(null, { status: 404 });
    const catalog = await realpath(documentationRoot());
    const project = await realpath(path.join(catalog, parts[0]));
    if (!project.startsWith(catalog + path.sep)) return new Response(null, { status: 404 });
    const root = await realpath(path.join(catalog, ...parts.slice(0, parts[1] === 'img' ? 2 : 3)));
    if (!root.startsWith(project + path.sep)) return new Response(null, { status: 404 });
    const imageParts = parts.slice(parts[1] === 'img' ? 2 : 3);
    const file = await realpath(path.join(root, ...imageParts));
    if (!file.startsWith(root + path.sep)) return new Response(null, { status: 404 });
    return new Response(new Uint8Array(await readFile(file)), { headers: { 'Content-Type': mime, 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'none'; sandbox", 'Cache-Control': 'public, max-age=300' } });
  } catch { return new Response(null, { status: 404 }); }
}
