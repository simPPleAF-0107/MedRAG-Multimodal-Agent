/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./frontend-web/index.html",
        "./frontend-web/src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Spatial Clinical Dashboard 2026
                obsidian: '#0A0A0A',
                surface: {
                    DEFAULT: '#111111',
                    2: '#161616',
                    3: '#1A1A1A',
                    4: '#202020',
                },
                // Brand: clinical cyan
                brand: {
                    50: '#e0fbff',
                    100: '#b3f5ff',
                    300: '#67e8f9',
                    400: '#22d3ee',
                    500: '#00D4FF',
                    600: '#0ea5e9',
                    700: '#0284c7',
                    900: '#0c4a6e',
                },
                // Confidence: Emerald (high), Amber (medium), Rose (critical)
                emerald: {
                    400: '#34d399',
                    500: '#10E8A0',
                    600: '#059669',
                },
                amber: {
                    400: '#fbbf24',
                    500: '#F5A623',
                    600: '#d97706',
                },
                rose: {
                    400: '#fb7185',
                    500: '#FF4567',
                    600: '#e11d48',
                },
                coral: {
                    500: '#FF2A7A',
                    600: '#e61e66',
                },
                danger: '#dc2626',
                warning: '#f59e0b',
                success: '#10E8A0',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
            letterSpacing: {
                tighter: '-0.04em',
                tight: '-0.02em',
                'clinical': '-0.01em',
            },
            backdropBlur: {
                'glass': '25px',
                'heavy': '40px',
            },
            boxShadow: {
                'neon': '0 0 15px rgba(0,212,255,0.5), 0 0 30px rgba(0,212,255,0.3)',
                'neon-emerald': '0 0 15px rgba(16,232,160,0.5), 0 0 30px rgba(16,232,160,0.3)',
                'neon-rose': '0 0 15px rgba(255,69,103,0.5)',
                'glass': '0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05)',
                'glass-hover': '0 16px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08)',
                'bento': '0 4px 24px rgba(0,0,0,0.4)',
                'neon-coral': '0 0 15px rgba(255,42,122,0.5)',
            },
            animation: {
                'scan-line': 'scanLine 1.8s ease-in-out',
                'shimmer': 'shimmer 2s ease-in-out infinite',
                'kg-pulse': 'kgPulse 2s ease-in-out infinite',
                'entity-pop': 'entityPop 0.3s cubic-bezier(0.34,1.56,0.64,1) both',
                'fade-up': 'fadeUp 0.4s cubic-bezier(0.16,1,0.3,1) both',
                'spring-in': 'springIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both',
                'slide-up-fade': 'slideUpFade 0.6s cubic-bezier(0.16,1,0.3,1) forwards',
                'pulse-glow': 'pulseGlow 4s ease-in-out infinite',
                'float': 'float 6s ease-in-out infinite',
                'blob': 'blob 7s infinite',
            },
            keyframes: {
                scanLine: {
                    '0%':   { transform: 'translateY(-100%)', opacity: '0' },
                    '10%':  { opacity: '1' },
                    '90%':  { opacity: '1' },
                    '100%': { transform: 'translateY(400%)', opacity: '0' },
                },
                shimmer: {
                    '0%':   { backgroundPosition: '-200% center' },
                    '100%': { backgroundPosition: '200% center' },
                },
                kgPulse: {
                    '0%, 100%': { opacity: '0.6', transform: 'scale(1)' },
                    '50%':      { opacity: '1',   transform: 'scale(1.08)' },
                },
                entityPop: {
                    '0%':   { opacity: '0', transform: 'scale(0.5) translateY(4px)' },
                    '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
                },
                fadeUp: {
                    '0%':   { opacity: '0', transform: 'translateY(12px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                springIn: {
                    '0%':   { opacity: '0', transform: 'scale(0.85)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
                slideUpFade: {
                    'from': { opacity: '0', transform: 'translateY(20px)' },
                    'to':   { opacity: '1', transform: 'translateY(0)' },
                },
                pulseGlow: {
                    '0%, 100%': { opacity: '1', boxShadow: '0 0 10px rgba(0,212,255,0.3)' },
                    '50%':      { opacity: '0.8', boxShadow: '0 0 25px rgba(0,212,255,0.7)' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%':      { transform: 'translateY(-12px)' },
                },
                blob: {
                    '0%':   { transform: 'translate(0,0) scale(1)' },
                    '33%':  { transform: 'translate(30px,-50px) scale(1.1)' },
                    '66%':  { transform: 'translate(-20px,20px) scale(0.9)' },
                    '100%': { transform: 'translate(0,0) scale(1)' },
                },
            },
            transitionTimingFunction: {
                'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
                'smooth': 'cubic-bezier(0.16, 1, 0.3, 1)',
            },
            transitionDuration: {
                'spring': '150ms',
            },
        },
    },
    plugins: [],
}
