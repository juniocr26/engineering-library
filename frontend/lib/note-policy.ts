/** Storage boundary, shared with Rails; parsing runs in a cancellable worker. */
export const NOTE_MAX_BYTES = 5 * 1024 * 1024;
export function noteUrl(url: string, key: string): string {
  const value = url.trim();
  if (/[\u0000-\u001f\u007f]/.test(value)) return '';
  if (/^(?:https?:|mailto:|tel:)/i.test(value)) return key === 'src' && !/^https?:/i.test(value) ? '' : value;
  if (key === 'src' && /^data:image\//i.test(value)) return value;
  if (/^[a-z][a-z\d+.-]*:/i.test(value)) return '';
  return value;
}
export function noteRenderError(source: string): string | null {
  return new TextEncoder().encode(source).length > NOTE_MAX_BYTES ? 'Preview supports at most 5 MiB. The original source is preserved.' : null;
}
