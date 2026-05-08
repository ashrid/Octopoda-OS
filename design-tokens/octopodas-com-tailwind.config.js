/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
    colors: {
        primary: {
            '50': 'hsl(24, 95%, 97%)',
            '100': 'hsl(24, 95%, 94%)',
            '200': 'hsl(24, 95%, 86%)',
            '300': 'hsl(24, 95%, 76%)',
            '400': 'hsl(24, 95%, 64%)',
            '500': 'hsl(24, 95%, 50%)',
            '600': 'hsl(24, 95%, 40%)',
            '700': 'hsl(24, 95%, 32%)',
            '800': 'hsl(24, 95%, 24%)',
            '900': 'hsl(24, 95%, 16%)',
            '950': 'hsl(24, 95%, 10%)',
            DEFAULT: '#f97015'
        },
        secondary: {
            '50': 'hsl(25, 95%, 97%)',
            '100': 'hsl(25, 95%, 94%)',
            '200': 'hsl(25, 95%, 86%)',
            '300': 'hsl(25, 95%, 76%)',
            '400': 'hsl(25, 95%, 64%)',
            '500': 'hsl(25, 95%, 50%)',
            '600': 'hsl(25, 95%, 40%)',
            '700': 'hsl(25, 95%, 32%)',
            '800': 'hsl(25, 95%, 24%)',
            '900': 'hsl(25, 95%, 16%)',
            '950': 'hsl(25, 95%, 10%)',
            DEFAULT: '#fba66a'
        },
        accent: {
            '50': 'hsl(25, 40%, 97%)',
            '100': 'hsl(25, 40%, 94%)',
            '200': 'hsl(25, 40%, 86%)',
            '300': 'hsl(25, 40%, 76%)',
            '400': 'hsl(25, 40%, 64%)',
            '500': 'hsl(25, 40%, 50%)',
            '600': 'hsl(25, 40%, 40%)',
            '700': 'hsl(25, 40%, 32%)',
            '800': 'hsl(25, 40%, 24%)',
            '900': 'hsl(25, 40%, 16%)',
            '950': 'hsl(25, 40%, 10%)',
            DEFAULT: '#e8d6c9'
        },
        'neutral-50': '#ebebeb',
        'neutral-100': '#141414',
        'neutral-200': '#000000',
        'neutral-300': '#2c2421',
        'neutral-400': '#756157',
        'neutral-500': '#ffffff',
        'neutral-600': '#493d36',
        'neutral-700': '#988881',
        'neutral-800': '#fff5eb',
        'neutral-900': '#67554c',
        background: '#14141f',
        foreground: '#000000'
    },
    fontFamily: {
        sans: [
            'Inter',
            'sans-serif'
        ],
        body: [
            'Space Grotesk',
            'sans-serif'
        ]
    },
    fontSize: {
        '12': [
            '12px',
            {
                lineHeight: '16px'
            }
        ],
        '14': [
            '14px',
            {
                lineHeight: '20px'
            }
        ],
        '16': [
            '16px',
            {
                lineHeight: '24px'
            }
        ],
        '18': [
            '18px',
            {
                lineHeight: '28px'
            }
        ],
        '20': [
            '20px',
            {
                lineHeight: '28px',
                letterSpacing: '-0.5px'
            }
        ],
        '60': [
            '60px',
            {
                lineHeight: '60px',
                letterSpacing: '-1.5px'
            }
        ]
    },
    spacing: {
        '2': '4px',
        '20': '40px',
        '24': '48px',
        '32': '64px',
        '56': '112px'
    },
    borderRadius: {
        lg: '12px',
        xl: '24px'
    },
    boxShadow: {
        sm: 'rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.15) 0px 20px 60px -20px',
        lg: 'rgba(249, 112, 21, 0.5) 0px 8px 24px -8px'
    },
    screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px'
    },
    transitionDuration: {
        '150': '0.15s',
        '200': '0.2s'
    },
    transitionTimingFunction: {
        custom: 'cubic-bezier(0.4, 0, 0.2, 1)'
    },
    container: {
        center: true,
        padding: '48px'
    },
    maxWidth: {
        container: '1280px'
    }
},
  },
};
