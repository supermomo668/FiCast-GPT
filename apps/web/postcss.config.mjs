/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    'postcss-import': {},
    tailwindcss: {},
    autoprefixer: {}, // Ensure this line is present
  },
};

export default config;
