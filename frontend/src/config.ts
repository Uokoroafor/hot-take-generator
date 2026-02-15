/**
 * Application configuration
 * Loads environment variables and provides default fallbacks
 */

interface Config {
  apiBaseUrl: string;
}

const envApiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const storedApiBaseUrl =
  typeof window !== 'undefined' ? localStorage.getItem('apiBaseUrl') : null;
const isProduction = import.meta.env.PROD;

const config: Config = {
  apiBaseUrl: isProduction ? envApiBaseUrl : storedApiBaseUrl || envApiBaseUrl,
};

export default config;
