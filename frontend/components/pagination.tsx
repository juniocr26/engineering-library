import Link from '@/components/navigation-link';
import { pageNumbers } from '@/lib/pagination';
import { catalogHref, messages, type Language } from '@/lib/i18n';
export function Pagination({ page, total, language }: { page: number; total: number; language: Language }) {
  const t = messages[language];
  return <><nav className="pagination" aria-label={t.pagination}>{page === 1 ? <span aria-disabled="true" aria-label={t.previous}>‹</span> : <Link href={catalogHref(page - 1, language)} aria-label={t.previous}>‹</Link>}{pageNumbers(page, total).map((n, i) => n === 'ellipsis' ? <span className="ellipsis" key={`gap-${i}`} aria-hidden="true">…</span> : <Link key={n} href={catalogHref(n, language)} aria-label={`${t.page} ${n}`} aria-current={page === n ? 'page' : undefined}>{n}</Link>)}{page === total ? <span aria-disabled="true" aria-label={t.next}>›</span> : <Link href={catalogHref(page + 1, language)} aria-label={t.next}>›</Link>}</nav><p className="page-count">{t.page} {page} {t.of} {total}</p></>;
}
