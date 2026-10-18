import { backend } from '@/lib/catalog';
export async function GET(_request: Request, { params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return new Response(null, { status: 404 });
  try {
    const response = await fetch(`${backend}/api/projects/${slug}/icon`, { signal: AbortSignal.timeout(3000) });
    if (!response.ok) return new Response(null, { status: 404 });
    return new Response(await response.text(), { headers: { 'Content-Type': 'image/svg+xml', 'Content-Security-Policy': "default-src 'none'; sandbox", 'X-Content-Type-Options': 'nosniff' } });
  } catch { return new Response(null, { status: 404 }); }
}
