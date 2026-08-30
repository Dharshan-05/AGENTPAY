export const tokens = {
  colors: {
    background: {
      primary: '#09090B',
      secondary: '#131316',
      tertiary: '#1A1A1F',
      elevated: '#222227',
    },
    accent: {
      primary: '#0B827A',
      secondary: '#0A6D65',
      muted: '#085853',
      glow: 'rgba(11, 130, 122, 0.15)',
    },
    border: {
      subtle: 'rgba(255,255,255,0.06)',
      default: 'rgba(255,255,255,0.08)',
      strong: 'rgba(255,255,255,0.12)',
      accent: 'rgba(11, 130, 122, 0.3)',
    },
    text: {
      primary: '#FAFAFA',
      secondary: '#A0A0AB',
      muted: '#61616A',
      inverse: '#09090B',
    },
    status: {
      critical: '#EF4444',
      high: '#F97316',
      medium: '#EAB308',
      low: '#22C55E',
      info: '#3B82F6',
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    '2xl': '32px',
    '3xl': '48px',
  },
  radius: {
    sm: '6px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
  shadow: {
    card: '0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)',
    elevated: '0 4px 6px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)',
    modal: '0 10px 25px rgba(0,0,0,0.5)',
    glow: '0 0 20px rgba(11, 130, 122, 0.15)',
  },
} as const