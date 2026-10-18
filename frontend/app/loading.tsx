 'use client';
import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { BookLayout } from '@/components/book-layout';
import { CatalogState } from '@/components/catalog-state';
import { languageOf } from '@/lib/i18n';
function LoadingBook() {
  const params = useSearchParams();
  const language = languageOf(params.get('lang') ?? undefined);
  return <BookLayout language={language}><CatalogState kind="loading" language={language}/></BookLayout>;
}
export default function Loading() { return <Suspense><LoadingBook/></Suspense>; }
