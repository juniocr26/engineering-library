import 'server-only';
import { lstat, readFile, realpath, readdir, stat } from 'node:fs/promises';
import path from 'node:path';

export function localCatalogManagement(headers: Headers): boolean {
  const host = headers.get('host') ?? '';
  if (!/^(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(host)) return false;
  if (headers.has('forwarded')) return false;
  const forwardedHost = headers.get('x-forwarded-host');
  if (forwardedHost && forwardedHost !== host) return false;
  const forwarded = headers.get('x-forwarded-for');
  // Published loopback ports reach the container through the Docker host gateway.
  const localPeer = (value: string) => {
    const peer = value.trim().replace(/^::ffff:/, '');
    return ['127.0.0.1', '::1', '192.168.65.1', '192.168.65.254'].includes(peer) || /^172\.(1[6-9]|2\d|3[01])\.\d+\.1$/.test(peer);
  };
  return !forwarded || forwarded.split(',').every(localPeer);
}

export async function catalogManagementKey(): Promise<string> {
  const root = await realpath(process.env.DOCUMENTATION_ROOT ?? '/docs');
  let state = path.resolve(root, '../backend/storage/makedocs/runtime');
  if (root === '/docs') {
    const own = await stat(path.join(process.cwd(), 'package.json'), { bigint: true });
    const matches: string[] = [];
    for (const directory of await readdir('/sources', { withFileTypes: true })) {
      if (!directory.isDirectory() || directory.isSymbolicLink()) continue;
      const source = path.join('/sources', directory.name);
      try {
        const candidate = await lstat(path.join(source, 'frontend/package.json'), { bigint: true });
        if (!candidate.isSymbolicLink() && candidate.dev === own.dev && candidate.ino === own.ino) matches.push(source);
      } catch { /* Only a proven alias of this frontend can supply its backend key. */ }
    }
    if (matches.length !== 1) throw new Error('Backend storage is unavailable or ambiguous');
    state = path.join(matches[0], 'backend/storage/makedocs/runtime');
  }
  if ((await lstat(state)).isSymbolicLink()) throw new Error('Unsafe state');
  const target = path.join(state, 'management.key');
  if ((await lstat(target)).isSymbolicLink()) throw new Error('Unsafe key');
  const key = (await readFile(target, 'utf8')).trim();
  if (!/^[a-f0-9]{64}$/.test(key)) throw new Error('Invalid key');
  return key;
}
