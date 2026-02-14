/**
 * Application configuration
 * Loads environment variables and provides default fallbacks
 */

interface Config {
  apiBaseUrl: string;
}

const config: Config = {
  apiBaseUrl:
    (typeof window !== 'undefined' ? localStorage.getItem('apiBaseUrl') : null) ||
    import.meta.env.VITE_API_BASE_URL ||
    'http://localhost:8000',
};

export default config;
