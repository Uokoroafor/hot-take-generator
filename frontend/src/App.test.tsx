import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

// Mock fetch globally
global.fetch = vi.fn();

// Mock config module
vi.mock('./config', () => ({
  default: {
    apiBaseUrl: 'http://localhost:8000',
  },
}));

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the app with navigation layout', () => {
    render(<App />);

    // Check that the navigation brand is present
    const brandLink = screen.getByRole('link', { name: /🔥 hot take generator/i });
    expect(brandLink).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    render(<App />);

    // Check that all navigation links are present
    expect(screen.getByRole('link', { name: /generate/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /history/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /styles/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /agents/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /sources/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /settings/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /about/i })).toBeInTheDocument();
  });

  it('redirects to /generate by default and renders HotTakeGenerator', async () => {
    render(<App />);

    // Wait for the redirect and check that the form from HotTakeGenerator is present
    await waitFor(() => {
      expect(screen.getByLabelText(/topic/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/style/i)).toBeInTheDocument();
    });
  });

  it('has correct structure with nav and main sections', () => {
    const { container } = render(<App />);

    const nav = container.querySelector('.main-nav');
    const main = container.querySelector('.main-content');

    expect(nav).toBeInTheDocument();
    expect(main).toBeInTheDocument();
  });
});
