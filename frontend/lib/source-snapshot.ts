import { realpath, readFile, stat } from 'node:fs/promises';
import path from 'node:path';
/** Offline generator only. A project approval never grants arbitrary filesystem access. */
export async function approvedSource(root: string | undefined, relative: string): Promise<{ status: 'available'; content: Buffer } | { status: 'excluded' | 'missing' }> {
  if (!relative || path.isAbsolute(relative) || /[\\\0]/.test(relative) || relative.split('/').some(part => !part || part === '.' || part === '..')) return { status: 'excluded' };
  if (/(^|\/)(?:\.[^/]+|node_modules|vendor|target|dist|build|coverage|credentials|secrets)(\/|$)/i.test(relative) || !/\.(?:rs|go|py|rb|[jt]sx?|java|cs|php|sh|sql)$/.test(relative)) return { status: 'excluded' };
  if (!root) return { status: 'missing' };
  try {
    const base = await realpath(root);
    if (base !== path.resolve(root)) return { status: 'excluded' };
    const resolved = await realpath(path.join(base, relative));
    if (!resolved.startsWith(base + path.sep)) return { status: 'excluded' };
    const info = await stat(resolved);
    if (!info.isFile() || info.size > 512_000) return { status: 'excluded' };
    const content = await readFile(resolved);
    if (content.includes(0) || content.length > 512_000) return { status: 'excluded' };
    if (/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:ghp_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16})|(?:https?|postgres(?:ql)?|amqps?):\/\/[^\s/:]+:[^\s@${}]+@/.test(content.toString('utf8'))) return { status: 'excluded' };
    return { status: 'available', content };
  } catch { return { status: 'missing' }; }
}
