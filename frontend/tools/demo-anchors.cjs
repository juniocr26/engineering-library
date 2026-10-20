// Read-only validation against the same measured logical text used by the reader.
module.exports = async function inspectAnchors(page, documentId, language) {
  return page.evaluate(async ({ documentId, language }) => {
    const query = new URLSearchParams({ project: 'engineering-library', document: documentId, language });
    const read = async resource => {
      const response = await fetch(`/api/${resource}?${resource === 'bookmarks' ? new URLSearchParams({ project_slug: 'engineering-library', language }) : query}`, { cache: 'no-store' });
      if (!response.ok) throw Error(`${resource}: ${response.status}`);
      return (await response.json())[resource];
    };
    const [notes, highlights, bookmarks] = await Promise.all(['notes', 'highlights', 'bookmarks'].map(read));
    const blocks = new Map(Array.from(document.querySelectorAll('.reader-measure [data-highlight-block]')).map(block => [block.dataset.highlightBlock, block.textContent || '']));
    const valid = segment => {
      const text = blocks.get(segment.block);
      if (text === undefined || !segment.exact) return false;
      const matches = start => text.slice(start, start + segment.exact.length) === segment.exact && text.slice(Math.max(0, start - segment.prefix.length), start) === segment.prefix && text.slice(start + segment.exact.length, start + segment.exact.length + segment.suffix.length) === segment.suffix;
      if (text.slice(segment.start, segment.end) === segment.exact && matches(segment.start)) return true;
      let count = 0;
      for (let start = text.indexOf(segment.exact); start >= 0; start = text.indexOf(segment.exact, start + 1)) if (matches(start)) count++;
      return count === 1;
    };
    return [...notes.map(item => ({ ...item, kind: 'note' })), ...highlights.map(item => ({ ...item, kind: 'highlight' })), ...bookmarks.filter(item => item.document === documentId).map(item => ({ ...item, kind: 'bookmark' }))].map(item => ({
      id: item.id, kind: item.kind, document: documentId, language,
      anchor: item.anchor || item.segments[0].block,
      href: `${location.origin}/projects/engineering-library/docs/${documentId}?lang=${language}${item.kind === 'bookmark' ? '' : `&annotation=${item.kind}-${item.id}`}#${encodeURIComponent(item.anchor || item.segments[0].block)}`,
      valid: item.kind === 'bookmark' ? blocks.has(item.anchor) : item.segments.every(valid),
    }));
  }, { documentId, language });
};
