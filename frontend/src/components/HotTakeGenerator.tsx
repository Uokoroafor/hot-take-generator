import { useState, useEffect } from 'react';
import './HotTakeGenerator.css';
import config from '../config';

interface HotTakeResponse {
  hot_take: string;
  topic: string;
  style: string;
  agent_used: string;
  web_search_used?: boolean;
  news_context?: string;
}

interface SavedTake extends HotTakeResponse {
  id: string;
  savedAt: string;
}

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}

const HotTakeGenerator = () => {
  const [topic, setTopic] = useState('');
  const [style, setStyle] = useState('controversial');
  const [useWebSearch, setUseWebSearch] = useState(false);
  const [useNewsSearch, setUseNewsSearch] = useState(false);
  const [maxArticles, setMaxArticles] = useState(3);
  const [loading, setLoading] = useState(false);
  const [hotTake, setHotTake] = useState<HotTakeResponse | null>(null);
  const [error, setError] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [savedTakes, setSavedTakes] = useState<SavedTake[]>([]);
  const [defaultAgent, setDefaultAgent] = useState('');

  // Initialize dark mode from system preference
  useEffect(() => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedDarkMode = localStorage.getItem('darkMode');
    setDarkMode(savedDarkMode ? savedDarkMode === 'true' : prefersDark);
  }, []);

  // Apply dark mode class to document
  useEffect(() => {
    document.documentElement.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', darkMode.toString());
  }, [darkMode]);

  // Load saved takes from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('savedHotTakes');
    if (saved) {
      try {
        setSavedTakes(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load saved takes:', e);
      }
    }
  }, []);

  useEffect(() => {
    const savedDefaultAgent = localStorage.getItem('defaultAgent');
    if (savedDefaultAgent) {
      setDefaultAgent(savedDefaultAgent);
    }
  }, []);

  // Toast functions
  const showToast = (message: string, type: Toast['type'] = 'info') => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  };

  // Copy to clipboard
  const copyToClipboard = async () => {
    if (!hotTake) return;
    try {
      await navigator.clipboard.writeText(hotTake.hot_take);
      showToast('Copied to clipboard!', 'success');
    } catch {
      showToast('Failed to copy', 'error');
    }
  };

  // Share to X/Twitter
  const shareToTwitter = () => {
    if (!hotTake) return;
    const text = encodeURIComponent(`${hotTake.hot_take}\n\n#HotTake #${hotTake.topic.replace(/\s+/g, '')}`);
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank');
  };

  // Save hot take
  const saveHotTake = () => {
    if (!hotTake) return;
    const savedTake: SavedTake = {
      ...hotTake,
      id: Date.now().toString(),
      savedAt: new Date().toISOString(),
    };
    const updated = [savedTake, ...savedTakes];
    setSavedTakes(updated);
    localStorage.setItem('savedHotTakes', JSON.stringify(updated));
    showToast('Hot take saved!', 'success');
  };

  // Clear form
  const clearForm = () => {
    setTopic('');
    setHotTake(null);
    setError('');
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        clearForm();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const styles = [
    'controversial',
    'sarcastic',
    'optimistic',
    'pessimistic',
    'absurd',
    'analytical',
    'philosophical',
    'witty',
    'contrarian'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setError('');
    setHotTake(null);

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          style: style,
          agent_type: defaultAgent || undefined,
          use_web_search: useWebSearch,
          use_news_search: useNewsSearch,
          max_articles: maxArticles,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate hot take');
      }

      const data = await response.json();
      setHotTake(data);
      showToast('Hot take generated!', 'success');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hot-take-generator">
      {/* Dark Mode Toggle */}
      <div className="dark-mode-toggle">
        <button
          type="button"
          onClick={() => setDarkMode(!darkMode)}
          className="theme-toggle-btn"
          aria-label="Toggle dark mode"
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </div>

      {/* Toast Container */}
      <div className="toast-container" aria-live="polite" aria-atomic="true">
        {toasts.map(toast => (
          <div key={toast.id} className={`toast toast-${toast.type}`} role="alert">
            {toast.message}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="generator-form">
        <div className="form-group">
          <label htmlFor="topic">Topic:</label>
          <input
            type="text"
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a topic for your hot take..."
            aria-describedby="topic-help"
            required
          />
          <p id="topic-help" className="help-text visually-hidden">
            Enter any topic you want a hot take about
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="style">Style:</label>
          <select
            id="style"
            value={style}
            onChange={(e) => setStyle(e.target.value)}
          >
            {styles.map((s) => (
              <option key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="useWebSearch"
              checked={useWebSearch}
              onChange={(e) => setUseWebSearch(e.target.checked)}
              aria-describedby="web-search-help"
            />
            <label htmlFor="useWebSearch">
              🔍 Include web search results
            </label>
          </div>
          <p id="web-search-help" className="help-text">
            When enabled, relevant web search results will be included to provide broader context
          </p>
        </div>

        <div className="form-group">
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="useNewsSearch"
              checked={useNewsSearch}
              onChange={(e) => setUseNewsSearch(e.target.checked)}
              aria-describedby="news-search-help"
            />
            <label htmlFor="useNewsSearch">
              📰 Include recent news articles
            </label>
          </div>
          <p id="news-search-help" className="help-text">
            When enabled, recent news articles will be included to make your hot take more timely and relevant
          </p>
        </div>

        {useNewsSearch && (
          <div className="form-group">
            <label htmlFor="maxArticles">Number of news articles to include:</label>
            <select
              id="maxArticles"
              value={maxArticles}
              onChange={(e) => setMaxArticles(Number(e.target.value))}
            >
              <option value={1}>1 article</option>
              <option value={2}>2 articles</option>
              <option value={3}>3 articles</option>
              <option value={5}>5 articles</option>
            </select>
          </div>
        )}

        <button type="submit" disabled={loading || !topic.trim()}>
          {loading ? 'Generating...' : `Generate Hot Take ${useWebSearch || useNewsSearch ? '📰' : '🔥'}`}
        </button>
      </form>

      {/* Loading Skeleton */}
      {loading && (
        <div className="hot-take-result skeleton" role="status" aria-busy="true" aria-live="polite">
          <div className="skeleton-header"></div>
          <div className="skeleton-text"></div>
          <div className="skeleton-text"></div>
          <div className="skeleton-text short"></div>
          <div className="skeleton-metadata">
            <div className="skeleton-tag"></div>
            <div className="skeleton-tag"></div>
            <div className="skeleton-tag"></div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !hotTake && !error && (
        <div className="empty-state">
          <div className="empty-icon">🔥</div>
          <h3>Ready to Generate Some Hot Takes?</h3>
          <p>Enter a topic above and click the button to get started!</p>
          <p className="empty-hint">💡 Tip: Press <kbd>Esc</kbd> to clear the form anytime</p>
        </div>
      )}

      {/* Hot Take Result */}
      {hotTake && !loading && (
        <div className="hot-take-result">
          <div className="result-header">
            <h3>Your Hot Take:</h3>
            <div className="action-buttons">
              <button
                onClick={copyToClipboard}
                className="action-btn"
                aria-label="Copy to clipboard"
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
              <button
                onClick={shareToTwitter}
                className="action-btn"
                aria-label="Share on X/Twitter"
                title="Share on X/Twitter"
              >
                🐦 Tweet
              </button>
              <button
                onClick={saveHotTake}
                className="action-btn"
                aria-label="Save hot take"
                title="Save hot take"
              >
                💾 Save
              </button>
            </div>
          </div>
          <blockquote>{hotTake.hot_take}</blockquote>
          <div className="metadata">
            <p><strong>Topic:</strong> {hotTake.topic}</p>
            <p><strong>Style:</strong> {hotTake.style}</p>
            <p><strong>Generated by:</strong> {hotTake.agent_used}</p>
            {hotTake.web_search_used && (
              <p><strong>📰 News-enhanced:</strong> Yes</p>
            )}
          </div>

          {hotTake.news_context && (
            <details className="news-context">
              <summary>📰 News sources used</summary>
              <div className="news-content">
                <pre>{hotTake.news_context}</pre>
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  );
};

export default HotTakeGenerator;
