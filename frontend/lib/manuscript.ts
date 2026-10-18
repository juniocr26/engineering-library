/** Versioned, content-based seeds; never depends on translated labels or folio numbers. */
export function contentPageId(ids: readonly string[]) { return JSON.stringify([...new Set(ids)]); }
export function seededRandom(seed: string) {
  let state = 2166136261;
  for (const character of seed) state = Math.imul(state ^ character.charCodeAt(0), 16777619);
  return () => { state += 0x6d2b79f5; let n = state; n = Math.imul(n ^ n >>> 15, n | 1); n ^= n + Math.imul(n ^ n >>> 7, n | 61); return ((n ^ n >>> 14) >>> 0) / 4294967296; };
}
export function manuscriptMarks(project: string, identity: string, variant: string) {
  const random = seededRandom(JSON.stringify([project, identity, variant, 'v1']));
  return ['ink', 'wax', 'script', 'liquid', 'abrasion', ...(random() > .5 ? ['ink', 'script'] : [])].map((kind, index) => ({
    kind, edge: index % 2 ? 'right' : 'left', top: Math.round(random() * 85),
    size: Math.round(64 + random() * 60), rotation: Math.round(random() * 100 - 50), opacity: .3 + random() * .25,
  }));
}
