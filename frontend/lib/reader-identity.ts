// Coalesce first-reader cookie creation before concurrent annotation requests.
let identity: Promise<void> | undefined;
export function readerIdentity(project: string, language: string): Promise<void> {
  identity ??= fetch(`/api/bookmarks?project_slug=${encodeURIComponent(project)}&language=${language}`, { cache: 'no-store' }).then(response => {
    if (!response.ok) throw new Error('Reader identity unavailable');
  }).catch(error => { identity = undefined; throw error; });
  return identity;
}
