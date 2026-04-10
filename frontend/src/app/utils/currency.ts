export interface CurrencyInfo {
  code: string;
  symbol: string;
}

interface CurrencyConfig extends CurrencyInfo {
  inrPerUnit: number;
}

const COUNTRY_CURRENCY_MAP: Record<string, CurrencyConfig> = {
  IN: { code: 'INR', symbol: '₹', inrPerUnit: 1 },
  US: { code: 'USD', symbol: '$', inrPerUnit: 83 },
  UK: { code: 'GBP', symbol: '£', inrPerUnit: 105 },
  CA: { code: 'CAD', symbol: 'C$', inrPerUnit: 61 },
  AU: { code: 'AUD', symbol: 'A$', inrPerUnit: 54 },
  DE: { code: 'EUR', symbol: '€', inrPerUnit: 90 },
  FR: { code: 'EUR', symbol: '€', inrPerUnit: 90 },
  JP: { code: 'JPY', symbol: '¥', inrPerUnit: 0.56 },
};

export function getCurrencyInfo(country?: string): CurrencyInfo {
  const config = COUNTRY_CURRENCY_MAP[country?.toUpperCase() || ''] || { code: 'INR', symbol: '₹', inrPerUnit: 1 };
  return { code: config.code, symbol: config.symbol };
}

function getCurrencyConfig(country?: string): CurrencyConfig {
  return COUNTRY_CURRENCY_MAP[country?.toUpperCase() || ''] || { code: 'INR', symbol: '₹', inrPerUnit: 1 };
}

export function convertInrToCurrency(amountInInr: number, country?: string): number {
  const config = getCurrencyConfig(country);
  const divisor = config.inrPerUnit || 1;
  return amountInInr / divisor;
}

export function convertCurrencyToInr(amountInCurrency: number, country?: string): number {
  const config = getCurrencyConfig(country);
  const multiplier = config.inrPerUnit || 1;
  return amountInCurrency * multiplier;
}

export function formatCurrencyAmount(amount: number, country?: string): string {
  const currency = getCurrencyInfo(country);
  const converted = Math.round(convertInrToCurrency(amount, country));
  return `${currency.symbol}${Number.isFinite(converted) ? converted.toLocaleString('en-US') : '0'}`;
}

export function formatCurrencyPrice(price: string, country?: string): string {
  const amount = Number(price.replace(/[^\d.-]/g, ''));
  if (Number.isNaN(amount)) {
    return price;
  }
  return formatCurrencyAmount(amount, country);
}