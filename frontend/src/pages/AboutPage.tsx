import './Pages.css';

const AboutPage = () => {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>ℹ️ About</h1>
        <p>Hot Take Generator</p>
      </div>

      <div className="about-content">
        <section className="about-section">
          <h2>What is this?</h2>
          <p>
            The Hot Take Generator is a full-stack application that uses AI to generate
            spicy, controversial, and thought-provoking opinions on any topic you can think of.
          </p>
          <p>
            Inspired by <a href="https://www.le-grove.co.uk/s/the-arsenal-opinion-podcast">The Arsenal Opinion Podcast</a> and their "Hottest of Takes" segment,
            this tool captures that same spirit of bold, entertaining commentary using the
            power of AI language models.
          </p>
        </section>

        <section className="about-section">
          <h2>Features</h2>
          <ul className="features-list">
            <li>🤖 Multiple AI agents (OpenAI GPT & Anthropic Claude)</li>
            <li>🎨 Various hot take styles (controversial, sarcastic, optimistic, etc.)</li>
            <li>🔍 Web search integration for timely, context-aware takes</li>
            <li>📰 News search for current events</li>
            <li>🌙 Dark mode support</li>
            <li>💾 Save and manage your favorite hot takes</li>
            <li>⚙️ Customizable style presets</li>
            <li>📊 Agent performance monitoring</li>
          </ul>
        </section>

        <section className="about-section">
          <h2>Tech Stack</h2>
          <div className="tech-grid">
            <div className="tech-item">
              <h3>Frontend</h3>
              <ul>
                <li>React 19</li>
                <li>TypeScript</li>
                <li>Vite</li>
                <li>React Router</li>
              </ul>
            </div>
            <div className="tech-item">
              <h3>Backend</h3>
              <ul>
                <li>FastAPI (Python)</li>
                <li>OpenAI API</li>
                <li>Anthropic API</li>
                <li>Web Search APIs</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="about-section">
          <h2>Open Source</h2>
          <p>
            This project is open source and available on GitHub. Contributions, issues,
            and feature requests are welcome!
          </p>
          <div className="links-section">
            <a
              href="https://github.com/Uokoroafor/hot-take-generator"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
            >
              📦 View on GitHub
            </a>
            <a
              href="https://github.com/Uokoroafor/hot-take-generator/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              🐛 Report an Issue
            </a>
          </div>
        </section>

        <section className="about-section">
          <h2>Credits</h2>
          <p>
            Created by the Hot Take Generator contributors
          </p>
          <p className="help-text">
            Inspired by The Arsenal Opinion Podcast's "Hottest of Takes" segment.
          </p>
        </section>

        <section className="about-section">
          <h2>License</h2>
          <p>
            MIT License - Free to use, modify, and distribute.
          </p>
        </section>
      </div>
    </div>
  );
};

export default AboutPage;
