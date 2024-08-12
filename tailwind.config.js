/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './bloomy/templates/**/*.{html,js}',
  ],
  theme: {
    extend: {
      colors: {
        'preto': '#444344',
        'purpura': '#9A66A4',
        'laranja': '#E16B42',
        'amarelo': '#C6D758',
        'rosa': '#DB426F',
        'branco': '#FCFBF7',
      },
      fontSize: {
        '7xl': '5rem', // Puedes ajustar el tamaño según tus necesidades
        '8xl': '6rem', // Puedes ajustar el tamaño según tus necesidades
      },
    },
  },
  plugins: [],
};