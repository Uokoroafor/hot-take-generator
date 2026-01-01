import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HistoryPage from './HistoryPage';

const mockSavedTakes = [
  {
    id: '1',
    hot_take: 'AI will replace all developers by 2030!',
    topic: 'AI in Software',
    style: 'controversial',
    agent_used: 'gpt-4',
    savedAt: '2024-01-15T10:00:00Z',
    web_search_used: true,
  },
  {
    id: '2',
    hot_take: 'TypeScript is overrated',
    topic: 'TypeScript',
    style: 'sarcastic',
    agent_used: 'claude',
    savedAt: '2024-01-14T09:00:00Z',
    web_search_used: false,
  },
  {
    id: '3',
    hot_take: 'The future is bright for web development',
    topic: 'Web Development',
    style: 'optimistic',
    agent_used: 'gpt-4',
    savedAt: '2024-01-16T11:00:00Z',
    web_search_used: true,
  },
];

describe('HistoryPage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders the page header', () => {
    render(<HistoryPage />);

    expect(screen.getByRole('heading', { name: /📜 history/i })).toBeInTheDocument();
    expect(screen.getByText(/your saved hot takes/i)).toBeInTheDocument();
  });

  it('displays empty state when no hot takes are saved', () => {
    render(<HistoryPage />);

    expect(screen.getByText(/📭 no saved hot takes yet/i)).toBeInTheDocument();
    expect(screen.getByText(/generate and save some from the generate page!/i)).toBeInTheDocument();
  });

  it('loads and displays saved hot takes from localStorage', () => {
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    expect(screen.getByText('AI will replace all developers by 2030!')).toBeInTheDocument();
    expect(screen.getByText('TypeScript is overrated')).toBeInTheDocument();
    expect(screen.getByText('The future is bright for web development')).toBeInTheDocument();
  });

  it('displays topic for each saved take', () => {
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    expect(screen.getByText('AI in Software')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('Web Development')).toBeInTheDocument();
  });

  it('displays style and agent badges for each take', () => {
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    expect(screen.getAllByText('controversial').length).toBeGreaterThan(0);
    expect(screen.getAllByText('sarcastic').length).toBeGreaterThan(0);
    expect(screen.getAllByText('optimistic').length).toBeGreaterThan(0);
    expect(screen.getAllByText('gpt-4')).toHaveLength(2);
    expect(screen.getAllByText('claude').length).toBeGreaterThan(0);
  });

  it('displays news badge for takes with web search enabled', () => {
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const newsBadges = screen.getAllByText(/📰 news/i);
    expect(newsBadges).toHaveLength(2); // Two takes have web_search_used: true
  });

  it('filters hot takes by topic', async () => {
    const user = userEvent.setup();
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const topicInput = screen.getByLabelText(/filter by topic/i);
    await user.type(topicInput, 'TypeScript');

    expect(screen.getByText('TypeScript is overrated')).toBeInTheDocument();
    expect(screen.queryByText('AI will replace all developers by 2030!')).not.toBeInTheDocument();
    expect(screen.queryByText('The future is bright for web development')).not.toBeInTheDocument();
  });

  it('filters hot takes by style', async () => {
    const user = userEvent.setup();
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const styleSelect = screen.getByLabelText(/filter by style/i);
    await user.selectOptions(styleSelect, 'controversial');

    expect(screen.getByText('AI will replace all developers by 2030!')).toBeInTheDocument();
    expect(screen.queryByText('TypeScript is overrated')).not.toBeInTheDocument();
    expect(screen.queryByText('The future is bright for web development')).not.toBeInTheDocument();
  });

  it('shows "no hot takes match your filters" when filters return no results', async () => {
    const user = userEvent.setup();
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const topicInput = screen.getByLabelText(/filter by topic/i);
    await user.type(topicInput, 'NonexistentTopic');

    expect(screen.getByText(/🔍 no hot takes match your filters/i)).toBeInTheDocument();
  });

  it('sorts by date (newest first) by default', () => {
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    const { container } = render(<HistoryPage />);

    const takes = container.querySelectorAll('.take-card');

    // Newest (id: 3, Jan 16) should be first
    expect(takes[0]).toHaveTextContent('The future is bright for web development');
  });

  it('sorts by topic alphabetically when selected', async () => {
    const user = userEvent.setup();
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const sortSelect = screen.getByLabelText(/sort by/i);
    await user.selectOptions(sortSelect, 'topic');

    const takes = document.querySelectorAll('.take-card');

    // "AI in Software" should be first alphabetically
    expect(takes[0]).toHaveTextContent('AI in Software');
  });

  it('deletes a hot take when delete button is clicked', async () => {
    const user = userEvent.setup();
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const deleteButtons = screen.getAllByRole('button', { name: /delete hot take/i });
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      const savedData = localStorage.getItem('savedHotTakes');
      expect(savedData).toBeTruthy();
      if (savedData) {
        const parsed = JSON.parse(savedData);
        expect(parsed).toHaveLength(2); // One deleted
      }
    });
  });

  it('clears all hot takes when clear all button is clicked and confirmed', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const clearButton = screen.getByRole('button', { name: /clear all/i });
    await user.click(clearButton);

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete all saved hot takes?');
    expect(localStorage.getItem('savedHotTakes')).toBeNull();
    expect(screen.getByText(/📭 no saved hot takes yet/i)).toBeInTheDocument();

    confirmSpy.mockRestore();
  });

  it('does not clear when clear all is cancelled', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const clearButton = screen.getByRole('button', { name: /clear all/i });
    await user.click(clearButton);

    expect(confirmSpy).toHaveBeenCalled();
    expect(localStorage.getItem('savedHotTakes')).toBeTruthy();
    expect(screen.getByText('AI will replace all developers by 2030!')).toBeInTheDocument();

    confirmSpy.mockRestore();
  });

  it('does not show clear all button when no takes are saved', () => {
    render(<HistoryPage />);

    expect(screen.queryByRole('button', { name: /clear all/i })).not.toBeInTheDocument();
  });

  it('renders filter controls', () => {
    render(<HistoryPage />);

    expect(screen.getByLabelText(/filter by topic/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/filter by style/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sort by/i)).toBeInTheDocument();
  });

  it('shows all unique styles in style filter dropdown', () => {
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    const styleSelect = screen.getByLabelText(/filter by style/i) as HTMLSelectElement;
    const options = Array.from(styleSelect.options).map(opt => opt.value);

    expect(options).toContain('');
    expect(options).toContain('controversial');
    expect(options).toContain('sarcastic');
    expect(options).toContain('optimistic');
  });

  it('handles corrupted localStorage data gracefully', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    localStorage.setItem('savedHotTakes', 'invalid json');
    render(<HistoryPage />);

    expect(screen.getByText(/📭 no saved hot takes yet/i)).toBeInTheDocument();
    expect(consoleSpy).toHaveBeenCalledWith('Failed to load saved takes:', expect.any(Error));

    consoleSpy.mockRestore();
  });

  it('displays formatted dates for each take', () => {
    localStorage.setItem('savedHotTakes', JSON.stringify(mockSavedTakes));
    render(<HistoryPage />);

    // Dates should be formatted using toLocaleDateString
    const dates = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
    expect(dates.length).toBeGreaterThan(0);
  });
});
