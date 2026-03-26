/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
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
                sans: ['Outfit', 'sans-serif'],
            },
            boxShadow: {
                'neon': '0 0 10px rgba(69, 243, 255, 0.4)',
                'neon-coral': '0 0 10px rgba(255, 42, 122, 0.4)',
            }
        },
    },
    plugins: [],
}
