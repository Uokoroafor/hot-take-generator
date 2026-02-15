import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SourcesPage from './SourcesPage';

const mockSources = [
  {
    url: 'https://example.com/news1',
    title: 'Breaking News Article',
    snippet: 'This is a news article about current events',
    usedAt: '2024-01-15T10:00:00Z',
    type: 'news' as const,
  },
  {
    url: 'https://example.com/web1',
    title: 'Web Search Result',
    snippet: 'General web search result',
    usedAt: '2024-01-15T11:00:00Z',
    type: 'web' as const,
  },
  {
    url: 'https://example.com/news2',
    title: 'Another News Article',
    snippet: 'More breaking news',
    usedAt: '2024-01-14T09:00:00Z',
    type: 'news' as const,
  },
];

describe('SourcesPage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders the page header', () => {
    render(<SourcesPage />);

    expect(screen.getByRole('heading', { name: /📚 recent sources/i })).toBeInTheDocument();
    expect(screen.getByText(/web and news sources used in your hot takes/i)).toBeInTheDocument();
  });

  it('displays info box about feature development', () => {
    render(<SourcesPage />);

    expect(screen.getByText(/sources from hot takes generated with web\/news search are tracked/i)).toBeInTheDocument();
  });

  it('displays empty state when no sources are saved', () => {
    render(<SourcesPage />);

    expect(screen.getByText(/📭 no sources tracked yet/i)).toBeInTheDocument();
    expect(screen.getByText(/generate hot takes with web or news search enabled!/i)).toBeInTheDocument();
  });

  it('loads and displays sources from localStorage', () => {
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    expect(screen.getByText('Breaking News Article')).toBeInTheDocument();
    expect(screen.getByText('Web Search Result')).toBeInTheDocument();
    expect(screen.getByText('Another News Article')).toBeInTheDocument();
  });

  it('displays source snippets', () => {
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    expect(screen.getByText('This is a news article about current events')).toBeInTheDocument();
    expect(screen.getByText('General web search result')).toBeInTheDocument();
    expect(screen.getByText('More breaking news')).toBeInTheDocument();
  });

  it('renders filter tabs', () => {
    render(<SourcesPage />);

    expect(screen.getByRole('button', { name: /all sources/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /🔍 web/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /📰 news/i })).toBeInTheDocument();
  });

  it('filters sources by web type', async () => {
    const user = userEvent.setup();
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const webButton = screen.getByRole('button', { name: /🔍 web/i });
    await user.click(webButton);

    expect(screen.getByText('Web Search Result')).toBeInTheDocument();
    expect(screen.queryByText('Breaking News Article')).not.toBeInTheDocument();
    expect(screen.queryByText('Another News Article')).not.toBeInTheDocument();
  });

  it('filters sources by news type', async () => {
    const user = userEvent.setup();
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const newsButton = screen.getByRole('button', { name: /📰 news/i });
    await user.click(newsButton);

    expect(screen.getByText('Breaking News Article')).toBeInTheDocument();
    expect(screen.getByText('Another News Article')).toBeInTheDocument();
    expect(screen.queryByText('Web Search Result')).not.toBeInTheDocument();
  });

  it('shows all sources when all filter is selected', async () => {
    const user = userEvent.setup();
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const newsButton = screen.getByRole('button', { name: /📰 news/i });
    await user.click(newsButton);

    const allButton = screen.getByRole('button', { name: /all sources/i });
    await user.click(allButton);

    expect(screen.getByText('Breaking News Article')).toBeInTheDocument();
    expect(screen.getByText('Web Search Result')).toBeInTheDocument();
    expect(screen.getByText('Another News Article')).toBeInTheDocument();
  });

  it('highlights active filter tab', async () => {
    const user = userEvent.setup();
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const allButton = screen.getByRole('button', { name: /all sources/i });
    expect(allButton).toHaveClass('active');

    const webButton = screen.getByRole('button', { name: /🔍 web/i });
    await user.click(webButton);

    expect(webButton).toHaveClass('active');
    expect(allButton).not.toHaveClass('active');
  });

  it('displays clear all button when sources exist', () => {
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    expect(screen.getByRole('button', { name: /clear all/i })).toBeInTheDocument();
  });

  it('does not show clear all button when no sources exist', () => {
    render(<SourcesPage />);

    expect(screen.queryByRole('button', { name: /clear all/i })).not.toBeInTheDocument();
  });

  it('clears all sources when clear all is clicked and confirmed', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const clearButton = screen.getByRole('button', { name: /clear all/i });
    await user.click(clearButton);

    expect(confirmSpy).toHaveBeenCalledWith('Clear all recent sources?');
    expect(localStorage.getItem('recentSources')).toBeNull();
    expect(screen.getByText(/📭 no sources tracked yet/i)).toBeInTheDocument();

    confirmSpy.mockRestore();
  });

  it('does not clear sources when clear all is cancelled', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const clearButton = screen.getByRole('button', { name: /clear all/i });
    await user.click(clearButton);

    expect(confirmSpy).toHaveBeenCalled();
    expect(localStorage.getItem('recentSources')).toBeTruthy();
    expect(screen.getByText('Breaking News Article')).toBeInTheDocument();

    confirmSpy.mockRestore();
  });

  it('groups sources by date', () => {
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    // Should have date headers
    const dateHeaders = document.querySelectorAll('.sources-date');
    expect(dateHeaders.length).toBeGreaterThan(0);
  });

  it('displays source URLs as clickable links', () => {
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);

    // Check first source link
    expect(links[0]).toHaveAttribute('href', 'https://example.com/news1');
    expect(links[0]).toHaveAttribute('target', '_blank');
    expect(links[0]).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('displays type badges for each source', () => {
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const webBadges = screen.getAllByText(/🔍 web/i);
    const newsBadges = screen.getAllByText(/📰 news/i);

    expect(webBadges.length).toBeGreaterThan(0);
    expect(newsBadges.length).toBeGreaterThan(0);
  });

  it('shows no match message when filter returns no results', async () => {
    const user = userEvent.setup();
    localStorage.setItem('recentSources', JSON.stringify([mockSources[0]])); // Only news source
    render(<SourcesPage />);

    const webButton = screen.getByRole('button', { name: /🔍 web/i });
    await user.click(webButton);

    expect(screen.getByText(/🔍 no sources match your filter/i)).toBeInTheDocument();
  });

  it('handles corrupted localStorage data gracefully', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    localStorage.setItem('recentSources', 'invalid json');
    render(<SourcesPage />);

    expect(screen.getByText(/📭 no sources tracked yet/i)).toBeInTheDocument();
    expect(consoleSpy).toHaveBeenCalledWith('Failed to load sources:', expect.any(Error));

    consoleSpy.mockRestore();
  });

  it('displays source titles as links', () => {
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const titleLink = screen.getByRole('link', { name: 'Breaking News Article' });
    expect(titleLink).toHaveAttribute('href', 'https://example.com/news1');
  });

  it('maintains filter state when switching between tabs', async () => {
    const user = userEvent.setup();
    localStorage.setItem('recentSources', JSON.stringify(mockSources));
    render(<SourcesPage />);

    const webButton = screen.getByRole('button', { name: /🔍 web/i });
    await user.click(webButton);

    expect(screen.getByText('Web Search Result')).toBeInTheDocument();
    expect(screen.queryByText('Breaking News Article')).not.toBeInTheDocument();

    const newsButton = screen.getByRole('button', { name: /📰 news/i });
    await user.click(newsButton);

    expect(screen.getByText('Breaking News Article')).toBeInTheDocument();
    expect(screen.queryByText('Web Search Result')).not.toBeInTheDocument();
  });
});
