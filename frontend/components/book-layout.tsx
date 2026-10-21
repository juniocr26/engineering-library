import { normalizeCursiveLabel } from '../lib/cursive-headings';
/* eslint-disable @next/next/no-img-element */
import Link from '@/components/navigation-link';
import { ManuscriptDecorations } from './manuscript-decorations';
import { DocumentLanguage } from './document-language';
import { catalogHref, messages, type Language } from '@/lib/i18n';
export function LanguageSelector({ language, page, slug }: { language: Language; page: number; slug?: string }) {
  return <nav className="langs" aria-label={messages[language].language}>{(['pt-BR', 'en'] as const).map(lang => <Link key={lang} className="lang" href={catalogHref(page, lang, slug)} hrefLang={lang} aria-current={lang === language ? 'true' : undefined}><span className="flag" aria-hidden="true">{lang === 'en' ? '🇺🇸' : '🇧🇷'}</span>{lang === 'en' ? 'English' : 'Português'}</Link>)}</nav>;
}
export function BookLayout({ language, page = 1, slug, children }: { language: Language; page?: number; slug?: string; children: React.ReactNode }) {
  const t = messages[language];
  return <main className="scene" lang={language}><DocumentLanguage language={language}/><section className="book" aria-label="Engineering Library"><div className="page picture"><img src="/assets/writer-library.jpg" alt={t.alt} /><ManuscriptDecorations variant="illustration" /></div><div className="page paper manuscript-surface"><ManuscriptDecorations variant={slug ? 'reading' : 'catalog'} /><div className="content"><div className="brand-heading"><h1 className="brand">{normalizeCursiveLabel('Engineering Library')}</h1><img className="brand-quill" src="/assets/manuscript/ornaments/writing-quill.svg" alt="" aria-hidden="true" /></div><div className="flourish" aria-hidden="true">❦</div><LanguageSelector language={language} page={page} slug={slug}/><p className="intro">{t.intro}</p><img className="portrait-mobile" src="/assets/writer-library.jpg" alt={t.alt}/><div className="flourish" aria-hidden="true">✧</div>{children}</div></div></section></main>;
}
