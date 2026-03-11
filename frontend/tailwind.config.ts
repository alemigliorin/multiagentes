import type { Config } from 'tailwindcss'
import tailwindcssAnimate from 'tailwindcss-animate'

export default {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        'primary-foreground': 'var(--color-primary-foreground)',
        secondary: 'var(--color-secondary)',
        'secondary-foreground': 'var(--color-secondary-foreground)',
        background: 'var(--color-background)',
        'background-secondary': 'var(--color-background-secondary)',
        foreground: 'var(--color-foreground)',
        muted: 'var(--color-muted)',
        'muted-foreground': 'var(--color-muted-foreground)',
        accent: 'var(--color-accent)',
        'accent-foreground': 'var(--color-accent-foreground)',
        border: 'var(--color-border)',
        ring: 'var(--color-ring)',
        destructive: 'var(--color-destructive)',
        positive: 'var(--color-positive)',
        brand: 'var(--color-brand)',
        'brand-light': 'var(--color-brand-light)',
        card: 'var(--color-card)',
        'card-foreground': 'var(--color-card-foreground)',
        'sidebar-bg': 'var(--color-sidebar-bg)',
        'sidebar-border': 'var(--color-sidebar-border)',
        'sidebar-hover': 'var(--color-sidebar-hover)',
        'input-bg': 'var(--color-input-bg)',
        'input-border': 'var(--color-input-border)',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        geist: 'var(--font-geist-sans)',
        dmmono: 'var(--font-dm-mono)',
      },
      borderRadius: {
        xl: '12px',
        '2xl': '16px',
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.08)',
        'input': '0 2px 8px rgba(0,0,0,0.04)',
        'sidebar': '1px 0 0 var(--color-sidebar-border)',
      }
    }
  },
  plugins: [tailwindcssAnimate]
} satisfies Config
