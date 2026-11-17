import type { Language } from './i18n.ts';
export const languageDirectory = (language: Language) => language === 'en' ? 'en' : 'pt-br';
/** Collections are grouped by project; API language identifiers remain unchanged. */
export function collectionPath(project: string, relative: string) {
  return `${project}/${relative}`;
}
