import { useState, useEffect } from 'react';
import './Pages.css';

interface Source {
  url: string;
  title: string;
  snippet: string;
  usedAt: string;
  type: 'web' | 'news';
  source?: string;
  published?: string;
}

const SourcesPage = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [filter, setFilter] = useState<'all' | 'web' | 'news'>('all');

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = () => {
    const saved = localStorage.getItem('recentSources');
    if (saved) {
      try {
        setSources(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load sources:', e);
      }
    }
  };

  const clearSources = () => {
    if (window.confirm('Clear all recent sources?')) {
      setSources([]);
      localStorage.removeItem('recentSources');
    }
  };

  const filteredSources = sources.filter(source => {
    if (filter === 'all') return true;
    return source.type === filter;
  });

  const groupedByDate = filteredSources.reduce((acc, source) => {
    const date = new Date(source.usedAt).toLocaleDateString();
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(source);
    return acc;
  }, {} as Record<string, Source[]>);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📚 Recent Sources</h1>
        <p>Web and news sources used in your hot takes</p>
      </div>

      <div className="info-box">
        <p>
          Sources from hot takes generated with web/news search are tracked and stored locally.
        </p>
      </div>

      <div className="filters-section">
        <div className="filter-tabs">
          <button
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All Sources
          </button>
          <button
            className={filter === 'web' ? 'active' : ''}
            onClick={() => setFilter('web')}
          >
            🔍 Web
          </button>
          <button
            className={filter === 'news' ? 'active' : ''}
            onClick={() => setFilter('news')}
          >
            📰 News
          </button>
        </div>

        {sources.length > 0 && (
          <button onClick={clearSources} className="btn-danger">
            Clear All
          </button>
        )}
      </div>

      {filteredSources.length === 0 ? (
        <div className="empty-state">
          <p>
            {sources.length === 0
              ? '📭 No sources tracked yet. Generate hot takes with web or news search enabled!'
              : '🔍 No sources match your filter.'}
          </p>
        </div>
      ) : (
        <div className="sources-list">
          {Object.entries(groupedByDate).map(([date, dateSources]) => (
            <div key={date} className="sources-group">
              <h3 className="sources-date">{date}</h3>
              {dateSources.map((source, index) => (
                <div key={index} className="source-card">
                  <div className="source-header">
                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-title">
                      {source.title}
                    </a>
                    <span className={`badge badge-${source.type}`}>
                      {source.type === 'web' ? '🔍 Web' : '📰 News'}
                    </span>
                  </div>
                  <p className="source-snippet">{source.snippet}</p>
                  {(source.source || source.published) && (
                    <p className="help-text">
                      {source.source && <span>Source: {source.source}</span>}
                      {source.source && source.published && <span> • </span>}
                      {source.published && (
                        <span>
                          Published: {new Date(source.published).toLocaleDateString()}
                        </span>
                      )}
                    </p>
                  )}
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-link">
                    {source.url}
                  </a>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SourcesPage;
