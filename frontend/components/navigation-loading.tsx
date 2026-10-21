'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState, useTransition, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import type { Language } from '@/lib/i18n';

const NavigationContext = createContext<ReturnType<typeof useRouter> | null>(null);

/** A status surface, deliberately without dialog semantics or focus management. */
export function ParchmentLoading({ language }: { language: Language }) {
  return <div className="navigation-loading" role="status" aria-live="polite" aria-atomic="true" lang={language}>
    <div className="navigation-loading__paper paper">
      <svg className="navigation-loading__quill" viewBox="0 0 80 80" width="64" height="64" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <path d="M17 66 60 17M28 54C23 30 43 11 67 10c0 24-13 44-39 44Z" fill="#93633722"/>
        <path d="m39 41-1-16m10 5 12-1M13 69h38"/>
      </svg>
      <span>{language === 'en' ? 'Loading...' : 'Carregando...'}</span>
    </div>
  </div>;
}

export function NavigationLoadingProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [visible, setVisible] = useState(false);
  const [language, setLanguage] = useState<Language>('pt-BR');
  const navigate = useCallback((href: string, options: Parameters<typeof router.push>[1], replace = false) => {
    const target = new URL(href, window.location.href);
    if (target.pathname === window.location.pathname && target.search === window.location.search) {
      (replace ? router.replace : router.push)(href, options);
      return;
    }
    setLanguage(target.searchParams.get('lang') === 'en' ? 'en' : 'pt-BR');
    startTransition(() => (replace ? router.replace : router.push)(href, options));
  }, [router]);
  useEffect(() => {
    if (!pending) return;
    // Only presentation is delayed; completion is controlled by React's transition.
    const threshold = window.setTimeout(() => setVisible(true), 150);
    // Escape hatch for a stalled network/router, not a simulated completion signal.
    const watchdog = window.setTimeout(() => setVisible(false), 30000);
    return () => { clearTimeout(threshold); clearTimeout(watchdog); setVisible(false); };
  }, [pending]);
  const navigation = useMemo(() => ({ ...router,
    push: (href: string, options?: Parameters<typeof router.push>[1]) => navigate(href, options),
    replace: (href: string, options?: Parameters<typeof router.replace>[1]) => navigate(href, options, true),
  }), [router, navigate]);
  return <NavigationContext.Provider value={navigation}>{children}{pending && visible && <ParchmentLoading language={language}/>}</NavigationContext.Provider>;
}

export function useNavigationRouter() {
  const router = useContext(NavigationContext);
  if (!router) throw new Error('NavigationLoadingProvider is required');
  return router;
}
