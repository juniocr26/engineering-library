import { backend } from '@/lib/catalog';

/** Shared annotation proxy with same-origin mutation checks. */
async function proxy(request: Request, { params }: { params: Promise<{ id?: string[] }> }) {
  const { id = [] } = await params;
  if (id.length > 1 || (id.length === 1 && !/^\d+$/.test(id[0]))) return new Response(null, { status: 404 });
  if ((['DELETE', 'PATCH'].includes(request.method)) !== (id.length === 1)) return new Response(null, { status: 405 });
  if (request.method !== 'GET') {
    const origin = request.headers.get('origin');
    let sameOrigin = false;
    try { sameOrigin = !!origin && new URL(origin).host === request.headers.get('host') && ['http:', 'https:'].includes(new URL(origin).protocol); } catch { /* Malformed origins are rejected below. */ }
    if (!sameOrigin || request.headers.get('sec-fetch-site') === 'cross-site') return new Response(null, { status: 403 });
  }
  const headers = new Headers({ 'Content-Type': 'application/json' });
  for (const name of ['x-annotation-csrf']) { const value = request.headers.get(name); if (value) headers.set(name, value); }
  try {
    const body = ['POST', 'PATCH'].includes(request.method) ? await request.text() : undefined;
    if (body && new TextEncoder().encode(body).length > 32 * 1024 * 1024) return new Response(null, { status: 413 });
    const query = new URLSearchParams();
    const project = new URL(request.url).searchParams.get('project_slug');
    if (request.method === 'GET' && project !== null) query.set('project_slug', project);
    const language = new URL(request.url).searchParams.get('language');
    if (language !== null) query.set('language', language);
    for (const name of ['project', 'document']) { const value = new URL(request.url).searchParams.get(name); if (value !== null) query.set(name, value); }
    const suffix = query.size ? `?${query}` : '';
    const response = await fetch(`${backend}/api/notes${id.length ? `/${id[0]}` : ''}${suffix}`, { method: request.method, headers, body, cache: 'no-store', signal: AbortSignal.timeout(5000) });
    const outgoing = new Headers({ 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    return new Response(response.status === 204 ? null : await response.text(), { status: response.status, headers: outgoing });
  } catch { return Response.json({ error: 'Notes unavailable' }, { status: 503 }); }
}
export const GET = proxy;
export const POST = proxy;
export const DELETE = proxy;

export const PATCH = proxy;
