/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./frontend-web/index.html",
        "./frontend-web/src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    50: '#e0fbff',
                    100: '#b3f5ff',
                    500: '#45F3FF', // Neon Cyan
                    600: '#00d7e6',
                    700: '#00aab8',
                    900: '#00555c',
                },
                coral: {
                    500: '#FF2A7A', // Electric Coral
                    600: '#e61e66',
                },
                deepSpace: '#0B0C10',
                surface: '#1F2833',
                danger: '#dc2626',
                warning: '#f59e0b',
                success: '#10b981',
            },
            fontFamily: {
                sans: ['Outfit', 'sans-serif', 'Inter'],
            },
            boxShadow: {
                'neon': '0 0 15px rgba(69, 243, 255, 0.6), 0 0 30px rgba(69, 243, 255, 0.4)',
                'neon-coral': '0 0 15px rgba(255, 42, 122, 0.6), 0 0 30px rgba(255, 42, 122, 0.4)',
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
            },
            animation: {
                'blob': 'blob 7s infinite',
                'spin-slow': 'spin 8s linear infinite',
                'pulse-glow': 'pulseGlow 4s ease-in-out infinite',
            },
            keyframes: {
                blob: {
                    '0%': { transform: 'translate(0px, 0px) scale(1)' },
                    '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
                    '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
                    '100%': { transform: 'translate(0px, 0px) scale(1)' },
                },
                pulseGlow: {
                    '0%, 100%': { opacity: '1', boxShadow: '0 0 10px rgba(69, 243, 255, 0.3)' },
                    '50%': { opacity: '0.8', boxShadow: '0 0 25px rgba(69, 243, 255, 0.7)' },
                }
            }
        },
    },
    plugins: [],
}
