import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: '#030712',
          900: '#090D16',
          850: '#0E131F',
          800: '#141A29',
        },
        trust: {
          500: '#10B981',
          600: '#059669',
          400: '#34D399',
          glow: 'rgba(16, 185, 129, 0.15)',
        },
        sovereign: {
          500: '#3B82F6',
          600: '#2563EB',
          400: '#60A5FA',
          glow: 'rgba(59, 130, 246, 0.15)',
        },
        shield: {
          500: '#F59E0B',
          600: '#D97706',
        }
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'Inter', 'system-ui', 'sans-serif'],
        display: ['var(--font-display)', 'Space Grotesk', 'sans-serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'beam-flow': 'beam-flow 3s linear infinite',
      },
      keyframes: {
        'beam-flow': {
          '0%': { strokeDashoffset: '1000' },
          '100%': { strokeDashoffset: '0' },
        }
      }
    },
  },
  plugins: [],
};

export default config;
