import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Engineering Library', description: 'A home for engineering knowledge.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body>{children}</body></html>;
}
