import { backend } from '@/lib/catalog';
async function proxy(request: Request) {
  if (process.env.NODE_ENV !== 'development') return new Response(null, { status: 404 });
  const origin = request.headers.get('origin');
  if (!origin || new URL(origin).host !== request.headers.get('host') || request.headers.get('sec-fetch-site') === 'cross-site') return new Response(null, { status: 403 });
  const body = request.method === 'POST' ? await request.text() : undefined;
  if (body && body.length > 600000) return new Response(null, { status: 413 });
  const headers = new Headers({ 'Content-Type': 'application/json' });
  for (const name of ['cookie', 'x-reader-csrf']) { const value = request.headers.get(name); if (value) headers.set(name, value); }
  const response = await fetch(`${backend}/api/note_demos${new URL(request.url).search}`, { method: request.method, headers, body, cache: 'no-store' });
  return new Response(response.status === 204 ? null : await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
}
export const POST = proxy;
export const DELETE = proxy;
