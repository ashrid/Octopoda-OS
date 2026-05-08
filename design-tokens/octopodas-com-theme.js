// React Theme — extracted from https://octopodas.com/dashboard/shared
// Compatible with: Chakra UI, Stitches, Vanilla Extract, or any CSS-in-JS

/**
 * TypeScript type definition for this theme:
 *
 * interface Theme {
 *   colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    foreground: string;
    neutral50: string;
    neutral100: string;
    neutral200: string;
    neutral300: string;
    neutral400: string;
    neutral500: string;
    neutral600: string;
    neutral700: string;
    neutral800: string;
    neutral900: string;
 *   };
 *   fonts: {
    body: string;
 *   };
 *   fontSizes: {
    '12': string;
    '14': string;
    '16': string;
    '18': string;
    '20': string;
    '60': string;
 *   };
 *   space: {
    '4': string;
    '40': string;
    '48': string;
    '64': string;
    '112': string;
 *   };
 *   radii: {
    lg: string;
    xl: string;
 *   };
 *   shadows: {
    sm: string;
    lg: string;
 *   };
 *   states: {
 *     hover: { opacity: number };
 *     focus: { opacity: number };
 *     active: { opacity: number };
 *     disabled: { opacity: number };
 *   };
 * }
 */

export const theme = {
  "colors": {
    "primary": "#f97015",
    "secondary": "#fba66a",
    "accent": "#e8d6c9",
    "background": "#14141f",
    "foreground": "#000000",
    "neutral50": "#ebebeb",
    "neutral100": "#141414",
    "neutral200": "#000000",
    "neutral300": "#2c2421",
    "neutral400": "#756157",
    "neutral500": "#ffffff",
    "neutral600": "#493d36",
    "neutral700": "#988881",
    "neutral800": "#fff5eb",
    "neutral900": "#67554c"
  },
  "fonts": {
    "body": "'Space Grotesk', sans-serif"
  },
  "fontSizes": {
    "12": "12px",
    "14": "14px",
    "16": "16px",
    "18": "18px",
    "20": "20px",
    "60": "60px"
  },
  "space": {
    "4": "4px",
    "40": "40px",
    "48": "48px",
    "64": "64px",
    "112": "112px"
  },
  "radii": {
    "lg": "12px",
    "xl": "24px"
  },
  "shadows": {
    "sm": "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.15) 0px 20px 60px -20px",
    "lg": "rgba(249, 112, 21, 0.5) 0px 8px 24px -8px"
  },
  "states": {
    "hover": {
      "opacity": 0.08
    },
    "focus": {
      "opacity": 0.12
    },
    "active": {
      "opacity": 0.16
    },
    "disabled": {
      "opacity": 0.38
    }
  }
};

// MUI v5 theme
export const muiTheme = {
  "palette": {
    "primary": {
      "main": "#f97015",
      "light": "hsl(24, 95%, 68%)",
      "dark": "hsl(24, 95%, 38%)"
    },
    "secondary": {
      "main": "#fba66a",
      "light": "hsl(25, 95%, 85%)",
      "dark": "hsl(25, 95%, 55%)"
    },
    "background": {
      "default": "#14141f",
      "paper": "#fff5eb"
    },
    "text": {
      "primary": "#000000",
      "secondary": "#141414"
    }
  },
  "typography": {
    "fontFamily": "'Space Grotesk', sans-serif",
    "h1": {
      "fontSize": "60px",
      "fontWeight": "800",
      "lineHeight": "60px"
    },
    "h3": {
      "fontSize": "20px",
      "fontWeight": "700",
      "lineHeight": "28px"
    },
    "body1": {
      "fontSize": "16px",
      "fontWeight": "400",
      "lineHeight": "24px"
    },
    "body2": {
      "fontSize": "12px",
      "fontWeight": "500",
      "lineHeight": "16px"
    }
  },
  "shape": {
    "borderRadius": 12
  },
  "shadows": [
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.05) 0px 1px 2px 0px",
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.15) 0px 20px 60px -20px",
    "rgba(249, 112, 21, 0.5) 0px 8px 24px -8px"
  ]
};

export default theme;
