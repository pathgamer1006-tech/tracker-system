/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './fitnesstrack/templates/**/*.html',
    './security_management/templates/**/*.html',
    './fitness/templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'sidebar-dark': '#1E1E2D',   // Dark sidebar
        'bg-light': '#F3F4F6',       // Light gray background
        'brand-purple': '#6366F1',   // Primary brand purple
        'brand-orange': '#F97316',   // Accent coral orange
        'brand-blue': '#0EA5E9',     // Accent sky blue
        'card-white': '#FFFFFF',     // White cards
        'text-dark': '#1F2937',      // Dark headings
        'text-light': '#9CA3AF',     // Light gray secondary text
      },
      fontFamily: {
        sans: ['Poppins', 'Inter', 'sans-serif'],
      },
      borderRadius: {
        '3xl': '1.875rem',
        '4xl': '2rem',
      },
      borderRadius: {
        'xl': '1rem',  // Softer card edges
      },
    },
  },
  plugins: [],
}
