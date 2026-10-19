/** Notes are private untrusted Markdown. Only reviewed, bundled image assets load. */
export const NOTE_MAX_BYTES = 131072;
export const noteAssets = new Set(['/assets/project-fallback.svg', '/assets/notes/persistence.svg', '/assets/writer-library.jpg']);
export function noteUrl(url: string, key: string): string {
  if (key === 'src') return noteAssets.has(url) ? url : '';
  if (/^https?:\/\//i.test(url)) {
    try { const value = new URL(url); return value.username || value.password ? '' : value.href; } catch { return ''; }
  }
  return /^(#[A-Za-z0-9_.:%-]+|\/projects\/[A-Za-z0-9_./%?#=&-]+)$/.test(url) && !url.includes('..') ? url : '';
}
export function noteRenderError(source: string): string | null {
  if (new TextEncoder().encode(source).length > NOTE_MAX_BYTES) return 'Preview supports at most 128 KiB.';
  // Bound parser depth before parsing; source remains editable and saveable.
  if (source.split('\n').some(line => /^(?:\s*>){33}/.test(line) || /^\s{128}/.test(line))) return 'Preview nesting is limited to 32 levels.';
  if ((source.match(/^\s*```mermaid\b/gm) ?? []).length > 8) return 'Preview supports at most 8 diagrams.';
  return null;
}
export function diagramAllowed(source: string) {
  // Block frontmatter, init directives, click handlers and external resource syntax.
  return source.length <= 12000 && !/%%\{|^\s*---|\bclick\s|<|https?:|data:|javascript:|url\s*\(/im.test(source);
}

/** Bound the parsed tree as well as input, including alternate Markdown fences. */
export function noteTreeLimits() {
  return (tree: { type: string; children?: unknown[] }) => {
    let nodes = 0, diagrams = 0;
    const queue: { node: { type: string; lang?: string; children?: unknown[] }; depth: number }[] = [{ node: tree, depth: 0 }];
    while (queue.length) {
      const { node, depth } = queue.pop()!;
      if (++nodes > 12000 || depth > 32 || (node.type === 'table' && (node.children?.length ?? 0) > 1001) || (node.type === 'code' && node.lang === 'mermaid' && ++diagrams > 8)) throw Error('Note preview complexity exceeded');
      for (const child of node.children ?? []) queue.push({ node: child as typeof node, depth: depth + 1 });
    }
  };
}
