/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
    theme: {
        extend: {
            colors: {
                // ── LeukoScan brand palette ──────────────────────────────────
                primary: '#172F7C',   // Navy   — nav, headings, primary buttons
                secondary: '#2DC6B2',   // Teal   — card borders, section backgrounds
                accent: '#1CBDC9',   // Cyan   — hovers, active links, confidence bar
                success: '#A2F9AB',   // Mint   — result card background
                error: '#F0756C',   // Coral  — alerts, error states
            },
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
            },
            borderRadius: {
                '2xl': '1rem',
                '3xl': '1.5rem',
            },
            boxShadow: {
                card: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
            },
        },
    },
    plugins: [],
};
