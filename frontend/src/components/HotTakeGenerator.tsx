import { useState, useEffect } from 'react';
import './HotTakeGenerator.css';
import config from '../config';
import useDarkMode from '../hooks/useDarkMode';

interface HotTakeResponse {
  hot_take: string;
  topic: string;
  style: string;
  agent_used: string;
  web_search_used?: boolean;
  news_context?: string;
  sources?: SourceRecord[];
}

interface SourceRecord {
  type: 'web' | 'news';
  title: string;
  url: string;
  snippet?: string;
  source?: string;
  published?: string;
}

interface TrackedSource {
  url: string;
  title: string;
  snippet: string;
  usedAt: string;
  type: 'web' | 'news';
  source?: string;
  published?: string;
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
  const [webSearchProvider, setWebSearchProvider] = useState('');
  const [newsDays, setNewsDays] = useState(14);
  const [strictQualityMode, setStrictQualityMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hotTake, setHotTake] = useState<HotTakeResponse | null>(null);
  const [error, setError] = useState('');
  const [darkMode, setDarkMode] = useDarkMode();
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [savedTakes, setSavedTakes] = useState<SavedTake[]>([]);
  const [defaultAgent, setDefaultAgent] = useState('');

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
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank', 'noopener,noreferrer');
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
      const controller = new AbortController();
      const timeoutMs = 30000;
      const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
      let response: Response;

      try {
        response = await fetch(`${config.apiBaseUrl}/api/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          signal: controller.signal,
          body: JSON.stringify({
            topic: topic.trim(),
            style: style,
            agent_type: defaultAgent || undefined,
            use_web_search: useWebSearch,
            use_news_search: useNewsSearch,
            max_articles: maxArticles,
            web_search_provider: webSearchProvider || undefined,
            news_days: newsDays,
            strict_quality_mode: strictQualityMode,
          }),
        });
      } finally {
        window.clearTimeout(timeoutId);
      }

      if (!response.ok) {
        let message = 'Failed to generate hot take';
        try {
          const errorData = await response.json();
          if (errorData && typeof errorData.detail === 'string' && errorData.detail.trim()) {
            message = errorData.detail;
          }
        } catch {
          // Ignore JSON parsing errors and keep generic message
        }
        throw new Error(message);
      }

      const data = await response.json();
      setHotTake(data);
      saveRecentSources(data.sources);
      showToast('Hot take generated!', 'success');
    } catch (err) {
      let errorMessage = err instanceof Error ? err.message : 'An error occurred';
      if (err instanceof DOMException && err.name === 'AbortError') {
        errorMessage = 'Request timed out after 30 seconds. Please try again.';
      } else if (err instanceof TypeError) {
        errorMessage =
          'Network error. Check API URL, backend availability, or CORS settings.';
      }
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const saveRecentSources = (sources?: SourceRecord[]) => {
    if (!sources || sources.length === 0) return;

    const now = new Date().toISOString();
    const normalizedSources: TrackedSource[] = sources
      .filter((source) => source.title && source.url)
      .map((source) => ({
        type: source.type,
        title: source.title,
        url: source.url,
        snippet: source.snippet || '',
        source: source.source,
        published: source.published,
        usedAt: now,
      }));

    if (normalizedSources.length === 0) return;

    try {
      const existingRaw = localStorage.getItem('recentSources');
      const existingSources: TrackedSource[] = existingRaw ? JSON.parse(existingRaw) : [];
      const merged = [...normalizedSources, ...existingSources];
      const seen = new Set<string>();
      const deduped = merged.filter((source) => {
        const key = `${source.type}:${source.url}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
      localStorage.setItem('recentSources', JSON.stringify(deduped.slice(0, 100)));
    } catch (e) {
      console.error('Failed to save recent sources:', e);
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

        {useWebSearch && (
          <div className="form-group">
            <label htmlFor="webSearchProvider">Web search provider:</label>
            <select
              id="webSearchProvider"
              value={webSearchProvider}
              onChange={(e) => setWebSearchProvider(e.target.value)}
            >
              <option value="">Auto-select provider</option>
              <option value="brave">Brave</option>
              <option value="serper">Serper (Google)</option>
            </select>
          </div>
        )}

        {useNewsSearch && (
          <div className="form-group">
            <label htmlFor="newsDays">News recency window:</label>
            <select
              id="newsDays"
              value={newsDays}
              onChange={(e) => setNewsDays(Number(e.target.value))}
            >
              <option value={3}>Last 3 days</option>
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
            </select>
          </div>
        )}

        {(useWebSearch || useNewsSearch) && (
          <div className="form-group">
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="strictQualityMode"
                checked={strictQualityMode}
                onChange={(e) => setStrictQualityMode(e.target.checked)}
                aria-describedby="strict-quality-help"
              />
              <label htmlFor="strictQualityMode">
                Strict source quality mode
              </label>
            </div>
            <p id="strict-quality-help" className="help-text">
              Filters low-signal results and prioritizes stronger, more relevant sources
            </p>
          </div>
        )}

        {(useWebSearch || useNewsSearch) && (
          <div className="form-group">
            <label htmlFor="maxArticles">Number of sources to include:</label>
            <select
              id="maxArticles"
              value={maxArticles}
              onChange={(e) => setMaxArticles(Number(e.target.value))}
            >
              <option value={1}>1 source</option>
              <option value={2}>2 sources</option>
              <option value={3}>3 sources</option>
              <option value={5}>5 sources</option>
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
