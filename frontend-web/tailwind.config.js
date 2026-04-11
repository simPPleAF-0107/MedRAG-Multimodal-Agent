/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Brand palette aligned with the new light theme
                brand: {
                    50:  '#F0EDFF',
                    100: '#D9D2FF',
                    400: '#6B4FD4',
                    500: '#3A0CA3',  // Primary
                    600: '#2E0882',
                    700: '#220664',
                },
                secondary: {
                    400: '#5A73F0',
                    500: '#4361EE',  // Secondary
                    600: '#344ECC',
                },
                accent: {
                    cyan: '#4CC9F0',
                    mint: '#A3F7FF',
                },
                danger: '#E74C3C',
                warning: '#F1C40F',
                success: '#2ECC71',
                info: '#3498DB',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            },
            boxShadow: {
                'soft': '0 2px 6px rgba(0,0,0,0.05)',
                'lifted': '0 8px 24px rgba(0,0,0,0.08)',
                'primary': '0 4px 16px rgba(58,12,163,0.2)',
            },
        },
    },
    plugins: [],
}
