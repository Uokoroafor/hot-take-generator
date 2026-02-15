import { useState, useEffect, useCallback } from 'react';
import './Pages.css';
import useDarkMode from '../hooks/useDarkMode';

const SettingsPage = () => {
  const isProduction = import.meta.env.PROD;
  const defaultApiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const [apiBaseUrl, setApiBaseUrl] = useState('');
  const [darkMode, setDarkMode] = useDarkMode();
  const [telemetryOptIn, setTelemetryOptIn] = useState(false);
  const [safeMode, setSafeMode] = useState(false);
  const [saved, setSaved] = useState(false);

  const loadSettings = useCallback(() => {
    // API Base URL (from env or localStorage override)
    const savedApiUrl = localStorage.getItem('apiBaseUrl');
    setApiBaseUrl(!isProduction && savedApiUrl ? savedApiUrl : defaultApiBaseUrl);

    // Telemetry
    const savedTelemetry = localStorage.getItem('telemetryOptIn');
    setTelemetryOptIn(savedTelemetry === 'true');

    // Safe Mode
    const savedSafeMode = localStorage.getItem('safeMode');
    setSafeMode(savedSafeMode === 'true');
  }, [defaultApiBaseUrl, isProduction]);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const saveSettings = (values?: {
    apiBaseUrl?: string;
    telemetryOptIn?: boolean;
    safeMode?: boolean;
  }) => {
    const nextApiBaseUrl = values?.apiBaseUrl ?? apiBaseUrl;
    const nextTelemetryOptIn = values?.telemetryOptIn ?? telemetryOptIn;
    const nextSafeMode = values?.safeMode ?? safeMode;

    // Save API Base URL
    if (isProduction || nextApiBaseUrl === defaultApiBaseUrl) {
      localStorage.removeItem('apiBaseUrl');
    } else {
      localStorage.setItem('apiBaseUrl', nextApiBaseUrl);
    }

    // Save Telemetry
    localStorage.setItem('telemetryOptIn', nextTelemetryOptIn.toString());

    // Save Safe Mode
    localStorage.setItem('safeMode', nextSafeMode.toString());

    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const resetToDefaults = () => {
    if (window.confirm('Reset all settings to defaults?')) {
      localStorage.removeItem('apiBaseUrl');
      localStorage.removeItem('telemetryOptIn');
      localStorage.removeItem('safeMode');
      // Don't reset darkMode as it's user preference

      setApiBaseUrl(defaultApiBaseUrl);
      setTelemetryOptIn(false);
      setSafeMode(false);

      saveSettings({
        apiBaseUrl: defaultApiBaseUrl,
        telemetryOptIn: false,
        safeMode: false,
      });
    }
  };


  return (
    <div className="page-container">
      <div className="page-header">
        <h1>⚙️ Settings</h1>
        <p>Configure your Hot Take Generator</p>
      </div>

      <div className="settings-container">
        <section className="settings-section">
          <h2>API Configuration</h2>
          <div className="form-group">
            <label htmlFor="api-url">API Base URL:</label>
            <input
              type="url"
              id="api-url"
              value={apiBaseUrl}
              onChange={(e) => setApiBaseUrl(e.target.value)}
              placeholder="http://localhost:8000"
              disabled={isProduction}
            />
            <p className="help-text">
              {isProduction
                ? 'API URL is managed by deployment environment variables.'
                : 'The backend API endpoint. Changes require a page refresh to take effect.'}
            </p>
          </div>
        </section>

        <section className="settings-section">
          <h2>Appearance</h2>
          <div className="form-group">
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="dark-mode"
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
              />
              <label htmlFor="dark-mode">🌙 Enable Dark Mode</label>
            </div>
            <p className="help-text">
              Toggle dark mode on or off. Overrides system preference.
            </p>
          </div>
        </section>

        <section className="settings-section">
          <h2>Privacy & Safety</h2>

          <div className="form-group">
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="telemetry"
                checked={telemetryOptIn}
                onChange={(e) => setTelemetryOptIn(e.target.checked)}
              />
              <label htmlFor="telemetry">📊 Enable Usage Analytics</label>
            </div>
            <p className="help-text">
              Help improve the app by sharing anonymous usage data.
            </p>
          </div>

          <div className="form-group">
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="safe-mode"
                checked={safeMode}
                onChange={(e) => setSafeMode(e.target.checked)}
              />
              <label htmlFor="safe-mode">🛡️ Enable Safe Mode</label>
            </div>
            <p className="help-text">
              Filter potentially offensive or controversial content.
            </p>
          </div>
        </section>

        <section className="settings-section">
          <h2>Data Management</h2>
          <div className="data-management">
            <div className="data-item">
              <div>
                <strong>Saved Hot Takes</strong>
                <p className="help-text">Your saved hot takes are stored locally</p>
              </div>
              <button
                onClick={() => {
                  if (window.confirm('Delete all saved hot takes?')) {
                    localStorage.removeItem('savedHotTakes');
                    alert('Saved hot takes deleted');
                  }
                }}
                className="btn-danger"
              >
                Clear
              </button>
            </div>

            <div className="data-item">
              <div>
                <strong>Style Presets</strong>
                <p className="help-text">Custom style configurations</p>
              </div>
              <button
                onClick={() => {
                  if (window.confirm('Delete all custom style presets?')) {
                    localStorage.removeItem('stylePresets');
                    alert('Style presets deleted');
                  }
                }}
                className="btn-danger"
              >
                Clear
              </button>
            </div>
          </div>
        </section>

        <div className="settings-actions">
          <button onClick={() => saveSettings()} className="btn-primary">
            {saved ? '✓ Saved!' : 'Save Settings'}
          </button>
          <button onClick={resetToDefaults} className="btn-secondary">
            Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
