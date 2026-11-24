import { BookLayout } from '@/components/book-layout';
import { CatalogManager } from '@/components/catalog-manager';
import { headers } from 'next/headers';
import { localCatalogManagement } from '@/lib/catalog-management';
import { Pagination } from '@/components/pagination';
import { CatalogState } from '@/components/catalog-state';
import { catalogRequest, type CatalogPage } from '@/lib/catalog';
import { languageOf, messages } from '@/lib/i18n';
export const dynamic = 'force-dynamic';
export default async function Home({ searchParams }: { searchParams: Promise<{ lang?: string; page?: string }> }) {
  const params = await searchParams;
  const language = languageOf(params.lang);
  let data: CatalogPage;
  try { data = await catalogRequest<CatalogPage>(`?page=${encodeURIComponent(params.page ?? '1')}`, language); }
  catch { return <BookLayout language={language}><CatalogState kind="error" language={language}/></BookLayout>; }
  const { page, total_pages } = data.pagination;
  const enabled = localCatalogManagement(await headers());
  return <BookLayout language={language} page={page}><h2 className="section-title">{messages[language].projects}</h2><CatalogManager projects={data.projects} language={language} page={page} enabled={enabled}/><Pagination page={page} total={total_pages} language={language}/></BookLayout>;
}
