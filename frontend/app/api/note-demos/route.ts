import { backend } from '@/lib/catalog';
async function proxy(request: Request) {
  if (process.env.NODE_ENV !== 'development') return new Response(null, { status: 404 });
  const origin = request.headers.get('origin');
  if (request.method !== 'GET') {
    let sameOrigin = false;
    try { sameOrigin = !!origin && ['http:', 'https:'].includes(new URL(origin).protocol) && new URL(origin).host === request.headers.get('host'); } catch { /* Reject malformed origins. */ }
    if (!sameOrigin || request.headers.get('sec-fetch-site') === 'cross-site') return new Response(null, { status: 403 });
  }
  const body = request.method === 'POST' ? await request.text() : undefined;
  if (body && new TextEncoder().encode(body).length > 32 * 1024 * 1024) return new Response(null, { status: 413 });
  const headers = new Headers({ 'Content-Type': 'application/json' });
  for (const name of ['x-annotation-csrf']) { const value = request.headers.get(name); if (value) headers.set(name, value); }
  const response = await fetch(`${backend}/api/note_demos${new URL(request.url).search}`, { method: request.method, headers, body, cache: 'no-store' });
  return new Response(response.status === 204 ? null : await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
}
export const POST = proxy;
export const DELETE = proxy;

export const GET = proxy;
