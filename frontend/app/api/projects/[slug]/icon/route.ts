import { validProjectDirectory } from '@/lib/catalog-paths';
import { backend } from '@/lib/catalog';
export async function GET(_request: Request, { params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  if (!validProjectDirectory(slug)) return new Response(null, { status: 404 });
  try {
    const response = await fetch(`${backend}/api/projects/${encodeURIComponent(slug)}/icon`, { signal: AbortSignal.timeout(3000) });
    if (!response.ok) return new Response(null, { status: 404 });
    return new Response(await response.arrayBuffer(), { headers: { 'Content-Type': 'image/webp', 'Content-Security-Policy': "default-src 'none'; sandbox", 'X-Content-Type-Options': 'nosniff' } });
  } catch { return new Response(null, { status: 404 }); }
}
