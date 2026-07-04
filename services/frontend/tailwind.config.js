export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Cool near-white neutrals — panels/cards float above a greyer base
        bg: '#C8C8C8',
        panel: '#FBFBFC',
        card: '#FFFFFF',
        ink: {
          DEFAULT: '#1C1D1F',
          soft: '#63666B',
          faint: '#9AA0A6',
        },
        line: {
          DEFAULT: '#EBECED',
          strong: '#DEE0E2',
        },
        // Single locked accent — a clean, slightly cool blue
        accent: {
          50: '#EEF3FE',
          100: '#DCE8FD',
          200: '#BFD4FB',
          500: '#2E6BF0',
          600: '#1F57D6',
          700: '#1A47B4',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'Segoe UI', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      boxShadow: {
        soft: '0 1px 2px rgba(28, 29, 31, 0.05)',
        pop: '0 12px 34px -14px rgba(28, 29, 31, 0.22)',
        composer: '0 2px 10px -4px rgba(28, 29, 31, 0.10)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        pulse2: {
          '0%, 100%': { opacity: '0.35' },
          '50%': { opacity: '1' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '20%': { transform: 'translateX(-7px)' },
          '40%': { transform: 'translateX(6px)' },
          '60%': { transform: 'translateX(-4px)' },
          '80%': { transform: 'translateX(2px)' },
        },
        // Slow drift for the decorative glows on the brand panel
        float: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '50%': { transform: 'translate(14px, -18px) scale(1.08)' },
        },
        'rise-in': {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.35s ease-out both',
        'fade-in': 'fade-in 0.4s ease-out both',
        shake: 'shake 0.4s ease-in-out',
        float: 'float 9s ease-in-out infinite',
        'rise-in': 'rise-in 0.5s cubic-bezier(0.22,1,0.36,1) both',
      },
    },
  },
  plugins: [],
}
