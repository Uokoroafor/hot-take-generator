import { useState, useEffect } from 'react';
import './Pages.css';

interface SavedTake {
  id: string;
  hot_take: string;
  topic: string;
  style: string;
  agent_used: string;
  savedAt: string;
  web_search_used?: boolean;
}

const HistoryPage = () => {
  const [savedTakes, setSavedTakes] = useState<SavedTake[]>([]);
  const [filterTopic, setFilterTopic] = useState('');
  const [filterStyle, setFilterStyle] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'topic'>('date');

  useEffect(() => {
    loadSavedTakes();
  }, []);

  const loadSavedTakes = () => {
    const saved = localStorage.getItem('savedHotTakes');
    if (saved) {
      try {
        setSavedTakes(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load saved takes:', e);
      }
    }
  };

  const deleteTake = (id: string) => {
    const updated = savedTakes.filter(take => take.id !== id);
    setSavedTakes(updated);
    localStorage.setItem('savedHotTakes', JSON.stringify(updated));
  };

  const clearAll = () => {
    if (window.confirm('Are you sure you want to delete all saved hot takes?')) {
      setSavedTakes([]);
      localStorage.removeItem('savedHotTakes');
    }
  };

  const filteredTakes = savedTakes
    .filter(take => {
      const matchesTopic = !filterTopic || take.topic.toLowerCase().includes(filterTopic.toLowerCase());
      const matchesStyle = !filterStyle || take.style === filterStyle;
      return matchesTopic && matchesStyle;
    })
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.savedAt).getTime() - new Date(a.savedAt).getTime();
      }
      return a.topic.localeCompare(b.topic);
    });

  const uniqueStyles = Array.from(new Set(savedTakes.map(t => t.style)));

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📜 History</h1>
        <p>Your saved hot takes</p>
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="filter-topic">Filter by topic:</label>
          <input
            type="text"
            id="filter-topic"
            value={filterTopic}
            onChange={(e) => setFilterTopic(e.target.value)}
            placeholder="Search topics..."
          />
        </div>

        <div className="filter-group">
          <label htmlFor="filter-style">Filter by style:</label>
          <select
            id="filter-style"
            value={filterStyle}
            onChange={(e) => setFilterStyle(e.target.value)}
          >
            <option value="">All styles</option>
            {uniqueStyles.map(style => (
              <option key={style} value={style}>{style}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="sort-by">Sort by:</label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'topic')}
          >
            <option value="date">Date (newest first)</option>
            <option value="topic">Topic (A-Z)</option>
          </select>
        </div>

        {savedTakes.length > 0 && (
          <button onClick={clearAll} className="btn-danger">
            Clear All
          </button>
        )}
      </div>

      {filteredTakes.length === 0 ? (
        <div className="empty-state">
          <p>
            {savedTakes.length === 0
              ? '📭 No saved hot takes yet. Generate and save some from the Generate page!'
              : '🔍 No hot takes match your filters.'}
          </p>
        </div>
      ) : (
        <div className="takes-grid">
          {filteredTakes.map(take => (
            <div key={take.id} className="take-card">
              <div className="take-card-header">
                <span className="take-topic">{take.topic}</span>
                <button
                  onClick={() => deleteTake(take.id)}
                  className="btn-delete"
                  aria-label="Delete hot take"
                >
                  🗑️
                </button>
              </div>
              <blockquote className="take-content">{take.hot_take}</blockquote>
              <div className="take-metadata">
                <span className="badge">{take.style}</span>
                <span className="badge">{take.agent_used}</span>
                {take.web_search_used && <span className="badge">📰 News</span>}
                <span className="take-date">
                  {new Date(take.savedAt).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
