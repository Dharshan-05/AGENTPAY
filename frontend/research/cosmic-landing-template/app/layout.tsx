import type { Metadata } from 'next';
import { Space_Grotesk, Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const spaceGrotesk = Space_Grotesk({ subsets: ['latin'], variable: '--font-display', display: 'swap' });
const inter = Inter({ subsets: ['latin'], variable: '--font-sans', display: 'swap' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono', display: 'swap' });

export const metadata: Metadata = {
  metadataBase: new URL('https://arcanea.ai'),
  title: 'Arcanea Cosmic Landing — 12 Motion Primitives, Liquid Glass UI',
  description:
    'Premium dark landing template with 12 motion primitives, liquid glass UI, and cosmic design tokens. Next.js 16 + Framer Motion + Tailwind. MIT.',
  openGraph: {
    title: 'Arcanea Cosmic Landing',
    description: '12 motion primitives · Liquid glass · MIT · Fork freely',
    type: 'website',
    siteName: 'Arcanea',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Arcanea Cosmic Landing',
    description: '12 motion primitives · Liquid glass · MIT',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans bg-[#09090b] text-white antialiased">{children}</body>
    </html>
  );
}
