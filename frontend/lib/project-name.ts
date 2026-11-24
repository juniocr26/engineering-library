/** Resilient label when the catalog is unavailable; official names come from bios. */
export function projectDisplayName(slug: string, name?: string): string {
  if (name?.trim()) return name.trim();
  const acronyms = new Set(['api', 'cli', 'css', 'html', 'http', 'https', 'id', 'json', 'sql', 'ui', 'url', 'ux']);
  return slug.split('-').map(word => acronyms.has(word) ? word.toUpperCase() : word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}
