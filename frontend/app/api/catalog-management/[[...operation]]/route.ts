import { backend } from '@/lib/catalog';
import { catalogManagementKey, localCatalogManagement } from '@/lib/catalog-management';

async function proxy(request: Request, { params }: { params: Promise<{ operation?: string[] }> }) {
  if (!localCatalogManagement(request.headers)) return new Response(null, { status: 403 });
  const { operation = [] } = await params;
  if (operation.length > 1) return new Response(null, { status: 404 });
  const segment = operation[0];
  if (request.method === 'GET' && segment && segment !== 'directories' && !/^[a-f0-9]{32}$/.test(segment)) return new Response(null, { status: 404 });
  if (request.method === 'POST') {
    if (!segment || !['add', 'update', 'remove'].includes(segment)) return new Response(null, { status: 404 });
    const origin = request.headers.get('origin');
    try {
      if (!origin || new URL(origin).host !== request.headers.get('host') || !['http:', 'https:'].includes(new URL(origin).protocol) || request.headers.get('sec-fetch-site') === 'cross-site') return new Response(null, { status: 403 });
    } catch { return new Response(null, { status: 403 }); }
    if (!request.headers.get('content-type')?.startsWith('application/json')) return new Response(null, { status: 415 });
  }
  try {
    const body = request.method === 'POST' ? await request.text() : undefined;
    if (body && Buffer.byteLength(body) > 4096) return new Response(null, { status: 413 });
    const response = await fetch(`${backend}/api/catalog_management${segment ? `/${segment}` : ''}`, {
      method: request.method, body, headers: { 'Content-Type': 'application/json', 'X-Catalog-Key': await catalogManagementKey() },
      cache: 'no-store', signal: AbortSignal.timeout(10000),
    });
    return new Response(await response.text(), { status: response.status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
  } catch { return Response.json({ error: 'management_unavailable' }, { status: 503 }); }
}

export const GET = proxy;
export const POST = proxy;
