// Track exact POST response IDs. Failure cleanup must never delete a shared collection.
module.exports = function trackAnnotationRecords(context, base) {
  const pending = [];
  const records = new Map();
  const observe = response => {
    const request = response.request();
    const url = new URL(response.url());
    const match = url.pathname.match(/^\/api\/(notes|highlights|bookmarks)$/);
    if (request.method() !== 'POST' || !match || !response.ok()) return;
    pending.push((async () => {
      const item = await response.json();
      if (item.id) records.set(`${match[1]}/${item.id}`, { resource: match[1], item });
    })().catch(() => {}));
  };
  context.on('response', observe);
  return async () => {
    await Promise.all(pending);
    for (const { resource, item } of [...records.values()].sort((a, b) => Number(b.resource === 'notes') - Number(a.resource === 'notes'))) {
      try {
        const query = new URLSearchParams({ project: item.project, document: item.document, language: item.language });
        const response = await context.request.get(`${base}/api/highlights?${query}`);
        if (!response.ok()) continue;
        const { csrf_token } = await response.json();
        await context.request.delete(`${base}/api/${resource}/${item.id}?${query}`, { headers: { Origin: base, 'X-Annotation-CSRF': csrf_token } });
      } catch { /* Closed contexts cannot issue requests; completed tests remove their own fixtures. */ }
    }
    context.off('response', observe);
  };
};
