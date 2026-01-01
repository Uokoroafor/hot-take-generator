import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AgentsPage from './AgentsPage';

// Mock fetch globally
global.fetch = vi.fn();

// Mock config module
vi.mock('../config', () => ({
  default: {
    apiBaseUrl: 'http://localhost:8000',
  },
}));

const mockAgents = [
  {
    name: 'gpt-4',
    description: 'OpenAI GPT-4 model',
    model: 'gpt-4-turbo',
    avgResponseTime: 1200,
    lastUsed: '2024-01-15T10:00:00Z',
  },
  {
    name: 'claude',
    description: 'Anthropic Claude model',
    model: 'claude-3-opus',
    avgResponseTime: 1500,
    lastUsed: '2024-01-14T09:00:00Z',
  },
  {
    name: 'gpt-3.5',
    description: 'OpenAI GPT-3.5 model',
    model: 'gpt-3.5-turbo',
  },
];

describe('AgentsPage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders the page header', () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: [] }),
    });

    render(<AgentsPage />);

    expect(screen.getByRole('heading', { name: /🤖 ai agents/i })).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockImplementationOnce(
      () => new Promise(() => {}) // Never resolves
    );

    render(<AgentsPage />);

    expect(screen.getByText(/loading agents/i)).toBeInTheDocument();
  });

  it('fetches agents from API on mount', async () => {
    const mockFetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });
    global.fetch = mockFetch;

    render(<AgentsPage />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/agents');
    });
  });

  it('displays agents after successful fetch', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('gpt-4')).toBeInTheDocument();
      expect(screen.getByText('claude')).toBeInTheDocument();
      expect(screen.getByText('gpt-3.5')).toBeInTheDocument();
    });
  });

  it('displays agent descriptions', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('OpenAI GPT-4 model')).toBeInTheDocument();
      expect(screen.getByText('Anthropic Claude model')).toBeInTheDocument();
      expect(screen.getByText('OpenAI GPT-3.5 model')).toBeInTheDocument();
    });
  });

  it('displays agent model information', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('gpt-4-turbo')).toBeInTheDocument();
      expect(screen.getByText('claude-3-opus')).toBeInTheDocument();
      expect(screen.getByText('gpt-3.5-turbo')).toBeInTheDocument();
    });
  });

  it('displays average response time when available', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('1200ms')).toBeInTheDocument();
      expect(screen.getByText('1500ms')).toBeInTheDocument();
    });
  });

  it('displays last used date when available', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      const dates = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
      expect(dates.length).toBeGreaterThan(0);
    });
  });

  it('shows empty state when no agents are available', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: [] }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText(/no agents available/i)).toBeInTheDocument();
      expect(screen.getByText(/check your api configuration/i)).toBeInTheDocument();
    });
  });

  it('handles fetch error gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Network error'));

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText(/no agents available/i)).toBeInTheDocument();
    });

    consoleSpy.mockRestore();
  });

  it('loads default agent from localStorage', async () => {
    localStorage.setItem('defaultAgent', 'claude');
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      const infoBox = document.querySelector('.info-box');
      expect(infoBox).toBeInTheDocument();
      expect(infoBox?.textContent).toContain('Default Agent:');
      expect(infoBox?.textContent).toContain('claude');
    });
  });

  it('displays "None selected" when no default agent is set', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      const infoBox = document.querySelector('.info-box');
      expect(infoBox).toBeInTheDocument();
      expect(infoBox?.textContent).toContain('Default Agent:');
      expect(infoBox?.textContent).toContain('None selected');
    });
  });

  it('shows default badge on default agent card', async () => {
    localStorage.setItem('defaultAgent', 'gpt-4');
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('Default')).toBeInTheDocument();
    });
  });

  it('sets agent as default when button is clicked', async () => {
    const user = userEvent.setup();
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('gpt-4')).toBeInTheDocument();
    });

    const setDefaultButtons = screen.getAllByRole('button', { name: /set as default/i });
    await user.click(setDefaultButtons[0]);

    expect(localStorage.getItem('defaultAgent')).toBeTruthy();
    expect(screen.getByText('Default')).toBeInTheDocument();
  });

  it('does not show set as default button for current default agent', async () => {
    localStorage.setItem('defaultAgent', 'gpt-4');
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      const agentCards = document.querySelectorAll('.agent-card');
      const gpt4Card = Array.from(agentCards).find(card =>
        card.textContent?.includes('gpt-4-turbo')
      );

      expect(gpt4Card?.textContent).toContain('Default');
      expect(gpt4Card?.querySelector('button[class*="btn-primary"]')).toBeNull();
    });
  });

  it('tests agent speed when test button is clicked', async () => {
    const user = userEvent.setup();
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ agents: mockAgents }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ hot_take: 'test', topic: 'test', style: 'controversial' }),
      });

    global.fetch = mockFetch;

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('gpt-4')).toBeInTheDocument();
    });

    const testButtons = screen.getAllByRole('button', { name: /⚡ test speed/i });
    await user.click(testButtons[0]);

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/generate',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: expect.stringContaining('"agent_type":"gpt-4"'),
      })
    );
  });

  it('shows testing state while testing agent', async () => {
    const user = userEvent.setup();
    (global.fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ agents: mockAgents }),
      })
      .mockImplementationOnce(
        () => new Promise(() => {}) // Never resolves for testing state
      );

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('gpt-4')).toBeInTheDocument();
    });

    const testButtons = screen.getAllByRole('button', { name: /⚡ test speed/i });
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /testing\.\.\./i })).toBeInTheDocument();
    });
  });

  it('disables test button while testing', async () => {
    const user = userEvent.setup();
    (global.fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ agents: mockAgents }),
      })
      .mockImplementationOnce(
        () => new Promise(() => {}) // Never resolves
      );

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('gpt-4')).toBeInTheDocument();
    });

    const testButtons = screen.getAllByRole('button', { name: /⚡ test speed/i });
    await user.click(testButtons[0]);

    await waitFor(() => {
      const testingButton = screen.getByRole('button', { name: /testing\.\.\./i });
      expect(testingButton).toBeDisabled();
    });
  });

  it('handles test agent error gracefully', async () => {
    const user = userEvent.setup();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    (global.fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ agents: mockAgents }),
      })
      .mockRejectedValueOnce(new Error('Test failed'));

    const { container } = render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText('gpt-4')).toBeInTheDocument();
    });

    const agentCards = container.querySelectorAll('.agent-card');
    const firstTestButton = agentCards[0].querySelector('button.btn-secondary');
    if (firstTestButton) {
      await user.click(firstTestButton);

      await waitFor(() => {
        expect(firstTestButton.textContent).toContain('Test Speed');
      });
    }

    consoleSpy.mockRestore();
  });

  it('displays help text about default agent', async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ agents: mockAgents }),
    });

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText(/the default agent will be used for generating hot takes/i)).toBeInTheDocument();
    });
  });
});
