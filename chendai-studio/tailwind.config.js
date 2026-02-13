/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#09090b", // Deepest black
                foreground: "#fafafa", // Almost white
                surface: "#18181b",    // Dark gray panel
                surfaceHighlight: "#27272a",
                border: "#27272a",
                primary: "#fbbf24",    // Amber/Gold
                primaryForeground: "#000000",
                secondary: "#a1a1aa",  // Zinc/Silver
                accent: "#f59e0b",     // Darker Gold
                muted: "#52525b",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'glass': 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)',
            },
        },
    },
    plugins: [],
}
