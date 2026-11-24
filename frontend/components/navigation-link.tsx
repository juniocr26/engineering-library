'use client';

import Link from 'next/link';
import type { ComponentProps } from 'react';
import { useNavigationRouter } from './navigation-loading';

/** Keep Next's prefetch, modifier-click, download and external-link handling. */
export default function NavigationLink({ onNavigate, ...props }: Omit<ComponentProps<typeof Link>, 'href'> & { href: string }) {
  const router = useNavigationRouter();
  return <Link {...props} onNavigate={event => {
    let prevented = false;
    onNavigate?.({ preventDefault: () => { prevented = true; event.preventDefault(); } });
    if (prevented) return;
    event.preventDefault();
    const href = props.href;
    (props.replace ? router.replace : router.push)(href, { scroll: props.scroll });
  }}/>;
}
