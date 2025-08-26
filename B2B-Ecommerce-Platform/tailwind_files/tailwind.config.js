/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/buyer/*html',
    '../templates/supplier/*html',
    '../templates/payments/*html',
    '../templates/manager/*html',
    '../templates/utils/*html',
    '../templates/auth_app/*html',
    '../venv/lib/python3.9/site-packages/allauth/templates/socialaccount',
  ],
  theme: {
    screens: {
        sm: '480px',
        md: '768px',
        lg: '976px',
        xl: '1440px',
    },
    extend: {
        colors: {
            yellowColor: 'hsl(38, 95%, 47%)',
            yellowColorHover: 'hsl(38, 95%, 44%)',
            backgroundColor: 'hsl(0, 0%, 9%)',
            lghterBackgroundColor: 'hsl(213, 28%, 19%)',
            lighterBackgroundColorHover: 'hsl(213, 28%, 14%)',
        },
        width: {
            'full': '100vh',
        },
        gridTemplateRows: {
            'auto-2': 'repeat(min-content, 2)',
            'auto-3': 'repeat(min-content, 3)',
        }
    }
},
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
