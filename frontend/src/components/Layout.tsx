import { Link, Outlet, useLocation } from 'react-router-dom';
import './Layout.css';

const Layout = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="app-layout">
      <nav className="main-nav">
        <div className="nav-container">
          <div className="nav-brand">
            <Link to="/" className="brand-link">
              🔥 Hot Take Generator
            </Link>
          </div>
          <ul className="nav-links">
            <li>
              <Link to="/generate" className={isActive('/generate') || isActive('/') ? 'active' : ''}>
                Generate
              </Link>
            </li>
            <li>
              <Link to="/history" className={isActive('/history') ? 'active' : ''}>
                History
              </Link>
            </li>
            <li>
              <Link to="/styles" className={isActive('/styles') ? 'active' : ''}>
                Styles
              </Link>
            </li>
            <li>
              <Link to="/agents" className={isActive('/agents') ? 'active' : ''}>
                Agents
              </Link>
            </li>
            <li>
              <Link to="/sources" className={isActive('/sources') ? 'active' : ''}>
                Sources
              </Link>
            </li>
            <li>
              <Link to="/settings" className={isActive('/settings') ? 'active' : ''}>
                Settings
              </Link>
            </li>
            <li>
              <Link to="/about" className={isActive('/about') ? 'active' : ''}>
                About
              </Link>
            </li>
          </ul>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
