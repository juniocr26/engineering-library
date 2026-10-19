import { backend } from '@/lib/catalog';

/** Same-origin proxy; the browser cookie remains HttpOnly and Rails owns its identity. */
async function proxy(request: Request, { params }: { params: Promise<{ id?: string[] }> }) {
  const { id = [] } = await params;
  if (id.length > 1 || (id.length === 1 && !/^\d+$/.test(id[0]))) return new Response(null, { status: 404 });
  if ((request.method === 'DELETE') !== (id.length === 1)) return new Response(null, { status: 405 });
  if (request.method !== 'GET') {
    const origin = request.headers.get('origin');
    let sameOrigin = false;
    try { sameOrigin = !!origin && new URL(origin).host === request.headers.get('host') && ['http:', 'https:'].includes(new URL(origin).protocol); } catch { /* Malformed origins are rejected below. */ }
    if (!sameOrigin || request.headers.get('sec-fetch-site') === 'cross-site') return new Response(null, { status: 403 });
  }
  const headers = new Headers({ 'Content-Type': 'application/json' });
  for (const name of ['cookie', 'x-reader-csrf']) { const value = request.headers.get(name); if (value) headers.set(name, value); }
  try {
    const body = request.method === 'POST' ? await request.text() : undefined;
    if (body && body.length > 4096) return new Response(null, { status: 413 });
    const query = new URLSearchParams();
    const project = new URL(request.url).searchParams.get('project_slug');
    if (request.method === 'GET' && project !== null) query.set('project_slug', project);
    const suffix = query.size ? `?${query}` : '';
    const response = await fetch(`${backend}/api/bookmarks${id.length ? `/${id[0]}` : ''}${suffix}`, { method: request.method, headers, body, cache: 'no-store', signal: AbortSignal.timeout(5000) });
    const outgoing = new Headers({ 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    for (const cookie of response.headers.getSetCookie()) outgoing.append('Set-Cookie', cookie);
    return new Response(response.status === 204 ? null : await response.text(), { status: response.status, headers: outgoing });
  } catch { return Response.json({ error: 'Bookmarks unavailable' }, { status: 503 }); }
}
export const GET = proxy;
export const POST = proxy;
export const DELETE = proxy;
