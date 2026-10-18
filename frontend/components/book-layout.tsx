/* eslint-disable @next/next/no-img-element */
import Link from 'next/link';
import { DocumentLanguage } from './document-language';
import { catalogHref, messages, type Language } from '@/lib/i18n';
export function LanguageSelector({ language, page, slug }: { language: Language; page: number; slug?: string }) {
  return <nav className="langs" aria-label={messages[language].language}>{(['pt-BR', 'en'] as const).map(lang => <Link key={lang} className="lang" href={catalogHref(page, lang, slug)} hrefLang={lang} aria-current={lang === language ? 'true' : undefined}><span className="flag" aria-hidden="true">{lang === 'en' ? '🇺🇸' : '🇧🇷'}</span>{lang === 'en' ? 'English' : 'Português'}</Link>)}</nav>;
}
export function BookLayout({ language, page = 1, slug, children }: { language: Language; page?: number; slug?: string; children: React.ReactNode }) {
  const t = messages[language];
  return <main className="scene" lang={language}><DocumentLanguage language={language}/><section className="book" aria-label="Engineering Library"><div className="page picture"><img src="/assets/writer-library.jpg" alt={t.alt} /></div><div className="page paper"><div className="decor" aria-hidden="true"/><div className="scar" aria-hidden="true"/><div className="inkmark" aria-hidden="true"/><div className="content"><h1 className="brand">Engineering Library</h1><div className="flourish" aria-hidden="true">❦</div><LanguageSelector language={language} page={page} slug={slug}/><p className="intro">{t.intro}</p><img className="portrait-mobile" src="/assets/writer-library.jpg" alt={t.alt}/><div className="flourish" aria-hidden="true">✧</div>{children}</div></div></section></main>;
}
