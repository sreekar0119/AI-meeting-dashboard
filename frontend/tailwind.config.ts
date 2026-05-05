import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#15304a',
        mist: '#eef4ff',
        brand: {
          50: '#f2f8ff',
          100: '#e0efff',
          200: '#bfdfff',
          300: '#91c8ff',
          400: '#5ca7f5',
          500: '#317fdd',
          600: '#1f67bf',
          700: '#1a5298',
          800: '#1a4479',
          900: '#19395f'
        },
        accent: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c'
        },
        success: {
          100: '#dcfce7',
          500: '#16a34a',
          700: '#166534'
        },
        warning: {
          100: '#fef3c7',
          500: '#d97706',
          700: '#92400e'
        },
        danger: {
          100: '#fee2e2',
          500: '#dc2626',
          700: '#991b1b'
        }
      },
      boxShadow: {
        panel: '0 24px 60px -32px rgba(21, 48, 74, 0.35)',
      },
      fontFamily: {
        sans: ['Manrope', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
