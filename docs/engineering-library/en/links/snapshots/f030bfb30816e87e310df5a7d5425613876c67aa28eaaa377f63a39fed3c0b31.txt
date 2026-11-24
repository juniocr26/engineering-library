import 'server-only';
import type { Language } from './i18n';
export type Project = { slug: string; name: string; description: string; categories?: { name: string; url: string }[] };
export type CatalogPage = { projects: Project[]; pagination: { page: number; total_pages: number; total_projects: number; page_size: number } };
export const backend = process.env.BACKEND_URL ?? 'http://backend:3000';
export async function catalogRequest<T>(path: string, language: Language): Promise<T> {
  const response = await fetch(`${backend}/api/projects${path}${path.includes('?') ? '&' : '?'}lang=${language}`, { cache: 'no-store', signal: AbortSignal.timeout(5000) });
  if (!response.ok) throw new Error('Catalog unavailable');
  return response.json() as Promise<T>;
}
