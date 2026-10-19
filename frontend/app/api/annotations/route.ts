import { backend } from '@/lib/catalog';

export async function GET(request: Request) {
  const headers = new Headers();
  const cookie = request.headers.get('cookie');
  if (cookie) headers.set('cookie', cookie);
  const query = new URL(request.url).searchParams;
  try {
    const response = await fetch(`${backend}/api/annotations?${query}`, { headers, cache: 'no-store', signal: AbortSignal.timeout(10000) });
    const outgoing = new Headers({ 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    for (const value of response.headers.getSetCookie()) outgoing.append('Set-Cookie', value);
    return new Response(await response.text(), { status: response.status, headers: outgoing });
  } catch { return Response.json({ error: 'Annotations unavailable' }, { status: 503 }); }
}
