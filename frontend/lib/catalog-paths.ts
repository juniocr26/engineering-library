import type { Language } from './i18n.ts';
export const languageDirectory = (language: Language) => language === 'en' ? 'en' : 'pt-br';
/** Collections are grouped by project; API language identifiers remain unchanged. */
export function collectionPath(project: string, relative: string) {
  return `${project}/${relative}`;
}

export function validProjectDirectory(value: string): boolean {
  return value.length >= 1 && value.length <= 255 && new TextEncoder().encode(value).length <= 255 && !/[ .]$/.test(value) &&
    !/[\x00-\x1f\x7f\\/:*?"<>|]/.test(value) && !/^(?:CON|PRN|AUX|NUL|(?:COM|LPT)[1-9])(?:[ .]|$)/i.test(value);
}
