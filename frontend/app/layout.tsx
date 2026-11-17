import { NavigationLoadingProvider } from '@/components/navigation-loading';
import type { Metadata } from 'next';
import './globals.css';
import appIcon from './icon.webp';
export const metadata: Metadata = { title: 'Engineering Library', description: 'A home for engineering knowledge.', icons: { icon: { url: appIcon.src, type: 'image/webp' } } };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body><NavigationLoadingProvider>{children}</NavigationLoadingProvider></body></html>;
}
