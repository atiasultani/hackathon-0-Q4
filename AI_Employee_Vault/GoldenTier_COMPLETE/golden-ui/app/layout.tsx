import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Gold Tier AI Employee - Vault Dashboard',
  description: 'Professional dashboard for managing your Gold Tier AI Employee system',
  keywords: ['AI Employee', 'Dashboard', 'Automation', 'Gold Tier'],
  authors: [{ name: 'AI Employee Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'noindex, nofollow',
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased bg-white dark:bg-gray-950 text-gray-900 dark:text-white`}>
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}