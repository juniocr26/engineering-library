import { collectionFile } from '@/lib/documentation';
const types: Record<string, string> = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml' };
export async function GET(_request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const mime = types[path.at(-1)?.split('.').at(-1)?.toLowerCase() ?? ''];
  const file = mime && await collectionFile(path[0], path.slice(1).join('/'));
  if (!file) return new Response(null, { status: 404 });
  return new Response(new Uint8Array(file), { headers: { 'Content-Type': mime, 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'none'; sandbox", 'Cache-Control': 'public, max-age=300' } });
}
