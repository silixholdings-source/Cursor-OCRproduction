export type Locale = 'en' | 'es' | 'fr' | 'de' | 'zh' | 'ja' | 'pt' | 'it';

export const locales: Locale[] = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'pt', 'it'];

export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, string> = {
  en: 'English',
  es: 'Español',
  fr: 'Français', 
  de: 'Deutsch',
  zh: '中文',
  ja: '日本語',
  pt: 'Português',
  it: 'Italiano'
};

export const localeFlags: Record<Locale, string> = {
  en: '🇺🇸',
  es: '🇪🇸', 
  fr: '🇫🇷',
  de: '🇩🇪',
  zh: '🇨🇳',
  ja: '🇯🇵',
  pt: '🇵🇹',
  it: '🇮🇹'
};


