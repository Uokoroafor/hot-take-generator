import { useState, useEffect } from 'react';
import './Pages.css';

interface StylePreset {
  id: string;
  name: string;
  tone: string;
  length: string;
  useEmojis: boolean;
  description: string;
}

const DEFAULT_STYLES: StylePreset[] = [
  { id: '1', name: 'Controversial', tone: 'bold and provocative', length: 'medium', useEmojis: false, description: 'Challenge conventional wisdom' },
  { id: '2', name: 'Sarcastic', tone: 'witty and sharp', length: 'short', useEmojis: true, description: 'Humor with a bite' },
  { id: '3', name: 'Optimistic', tone: 'positive and uplifting', length: 'medium', useEmojis: true, description: 'See the bright side' },
  { id: '4', name: 'Analytical', tone: 'deep and nuanced', length: 'long', useEmojis: false, description: 'Thorough breakdown' },
];

const StylesPage = () => {
  const [presets, setPresets] = useState<StylePreset[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    tone: '',
    length: 'medium',
    useEmojis: false,
    description: '',
  });

  useEffect(() => {
    loadPresets();
  }, []);

  const loadPresets = () => {
    const saved = localStorage.getItem('stylePresets');
    if (saved) {
      setPresets(JSON.parse(saved));
    } else {
      setPresets(DEFAULT_STYLES);
      localStorage.setItem('stylePresets', JSON.stringify(DEFAULT_STYLES));
    }
  };

  const savePresets = (newPresets: StylePreset[]) => {
    setPresets(newPresets);
    localStorage.setItem('stylePresets', JSON.stringify(newPresets));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingId) {
      const updated = presets.map(p => 
        p.id === editingId ? { ...formData, id: editingId } : p
      );
      savePresets(updated);
    } else {
      const newPreset: StylePreset = {
        ...formData,
        id: Date.now().toString(),
      };
      savePresets([...presets, newPreset]);
    }
    
    resetForm();
  };

  const editPreset = (preset: StylePreset) => {
    setFormData({
      name: preset.name,
      tone: preset.tone,
      length: preset.length,
      useEmojis: preset.useEmojis,
      description: preset.description,
    });
    setEditingId(preset.id);
    setShowForm(true);
  };

  const deletePreset = (id: string) => {
    if (window.confirm('Are you sure you want to delete this style preset?')) {
      savePresets(presets.filter(p => p.id !== id));
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      tone: '',
      length: 'medium',
      useEmojis: false,
      description: '',
    });
    setEditingId(null);
    setShowForm(false);
  };

  const resetToDefaults = () => {
    if (window.confirm('Reset to default styles? This will delete all custom presets.')) {
      savePresets(DEFAULT_STYLES);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🎨 Style Presets</h1>
        <p>Manage your hot take styles</p>
      </div>

      <div className="action-bar">
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? '✕ Cancel' : '+ Add Custom Style'}
        </button>
        <button onClick={resetToDefaults} className="btn-secondary">
          ↺ Reset to Defaults
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="preset-form">
          <h3>{editingId ? 'Edit Style' : 'New Style'}</h3>
          
          <div className="form-group">
            <label htmlFor="name">Style Name:</label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Philosophical"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="tone">Tone:</label>
            <input
              type="text"
              id="tone"
              value={formData.tone}
              onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
              placeholder="e.g., thoughtful and deep"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="length">Length:</label>
            <select
              id="length"
              value={formData.length}
              onChange={(e) => setFormData({ ...formData, length: e.target.value })}
            >
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
          </div>

          <div className="form-group">
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="useEmojis"
                checked={formData.useEmojis}
                onChange={(e) => setFormData({ ...formData, useEmojis: e.target.checked })}
              />
              <label htmlFor="useEmojis">Use emojis in hot takes</label>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe this style..."
              rows={3}
              required
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editingId ? 'Update Style' : 'Create Style'}
            </button>
            <button type="button" onClick={resetForm} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="presets-grid">
        {presets.map(preset => (
          <div key={preset.id} className="preset-card">
            <div className="preset-header">
              <h3>{preset.name}</h3>
              <div className="preset-actions">
                <button onClick={() => editPreset(preset)} className="btn-icon" title="Edit">
                  ✏️
                </button>
                <button onClick={() => deletePreset(preset.id)} className="btn-icon" title="Delete">
                  🗑️
                </button>
              </div>
            </div>
            <p className="preset-description">{preset.description}</p>
            <div className="preset-details">
              <span className="badge">Tone: {preset.tone}</span>
              <span className="badge">Length: {preset.length}</span>
              {preset.useEmojis && <span className="badge">😊 Emojis</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StylesPage;
