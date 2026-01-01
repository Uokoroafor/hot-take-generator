import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StylesPage from './StylesPage';

describe('StylesPage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders the page header', () => {
    render(<StylesPage />);

    expect(screen.getByRole('heading', { name: /🎨 style presets/i })).toBeInTheDocument();
    expect(screen.getByText(/manage your hot take styles/i)).toBeInTheDocument();
  });

  it('loads default style presets on first render', () => {
    render(<StylesPage />);

    expect(screen.getByText('Controversial')).toBeInTheDocument();
    expect(screen.getByText('Sarcastic')).toBeInTheDocument();
    expect(screen.getByText('Optimistic')).toBeInTheDocument();
    expect(screen.getByText('Analytical')).toBeInTheDocument();
  });

  it('saves default presets to localStorage on first render', () => {
    render(<StylesPage />);

    const saved = localStorage.getItem('stylePresets');
    expect(saved).toBeTruthy();
    if (saved) {
      const parsed = JSON.parse(saved);
      expect(parsed).toHaveLength(4);
      expect(parsed[0].name).toBe('Controversial');
    }
  });

  it('loads presets from localStorage if available', () => {
    const customPresets = [
      { id: '1', name: 'Custom Style', tone: 'unique', length: 'medium', useEmojis: true, description: 'Test' },
    ];
    localStorage.setItem('stylePresets', JSON.stringify(customPresets));

    render(<StylesPage />);

    expect(screen.getByText('Custom Style')).toBeInTheDocument();
    expect(screen.queryByText('Controversial')).not.toBeInTheDocument();
  });

  it('displays action buttons', () => {
    render(<StylesPage />);

    expect(screen.getByRole('button', { name: /\+ add custom style/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /↺ reset to defaults/i })).toBeInTheDocument();
  });

  it('shows form when add custom style button is clicked', async () => {
    const user = userEvent.setup();
    render(<StylesPage />);

    const addButton = screen.getByRole('button', { name: /\+ add custom style/i });
    await user.click(addButton);

    expect(screen.getByRole('heading', { name: /new style/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/style name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^tone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/length/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/use emojis in hot takes/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
  });

  it('hides form when cancel button is clicked', async () => {
    const user = userEvent.setup();
    render(<StylesPage />);

    const addButton = screen.getByRole('button', { name: /\+ add custom style/i });
    await user.click(addButton);

    expect(screen.getByRole('heading', { name: /new style/i })).toBeInTheDocument();

    const cancelButton = screen.getByRole('button', { name: /^cancel$/i });
    await user.click(cancelButton);

    expect(screen.queryByRole('heading', { name: /new style/i })).not.toBeInTheDocument();
  });

  it('toggles form visibility when add button is clicked again', async () => {
    const user = userEvent.setup();
    render(<StylesPage />);

    const addButton = screen.getByRole('button', {
      name: /(?:\+ add custom style|✕ cancel)/i,
    });
    await user.click(addButton);

    expect(screen.getByRole('heading', { name: /new style/i })).toBeInTheDocument();

    // Button text should change to "✕ Cancel"
    const cancelButton = screen.getByRole('button', { name: /✕ cancel/i });
    await user.click(cancelButton);

    expect(screen.queryByRole('heading', { name: /new style/i })).not.toBeInTheDocument();
  });

  it('creates a new style preset', async () => {
    const user = userEvent.setup();
    render(<StylesPage />);

    const addButton = screen.getByRole('button', { name: /\+ add custom style/i });
    await user.click(addButton);

    await user.type(screen.getByLabelText(/style name/i), 'Philosophical');
    await user.type(screen.getByLabelText(/^tone/i), 'deep and thoughtful');
    await user.selectOptions(screen.getByLabelText(/length/i), 'long');
    await user.click(screen.getByLabelText(/use emojis in hot takes/i));
    await user.type(screen.getByLabelText(/description/i), 'Explore deep concepts');

    const createButton = screen.getByRole('button', { name: /create style/i });
    await user.click(createButton);

    await waitFor(() => {
      expect(screen.getByText('Philosophical')).toBeInTheDocument();
      expect(screen.getByText('Explore deep concepts')).toBeInTheDocument();
    });
  });

  it('saves new preset to localStorage', async () => {
    const user = userEvent.setup();
    render(<StylesPage />);

    const addButton = screen.getByRole('button', { name: /\+ add custom style/i });
    await user.click(addButton);

    await user.type(screen.getByLabelText(/style name/i), 'TestStyle');
    await user.type(screen.getByLabelText(/^tone/i), 'test tone');
    await user.type(screen.getByLabelText(/description/i), 'test description');

    const createButton = screen.getByRole('button', { name: /create style/i });
    await user.click(createButton);

    await waitFor(() => {
      const saved = localStorage.getItem('stylePresets');
      expect(saved).toBeTruthy();
      if (saved) {
        const parsed = JSON.parse(saved);
        expect(parsed.length).toBeGreaterThan(4); // Default 4 + new one
        expect(parsed.some((p: { name: string }) => p.name === 'TestStyle')).toBe(true);
      }
    });
  });

  it('edits an existing style preset', async () => {
    const user = userEvent.setup();
    const { container } = render(<StylesPage />);

    const editButtons = container.querySelectorAll('button[title="Edit"]');
    await user.click(editButtons[0]);

    expect(screen.getByRole('heading', { name: /edit style/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/style name/i)).toHaveValue('Controversial');

    await user.clear(screen.getByLabelText(/style name/i));
    await user.type(screen.getByLabelText(/style name/i), 'Super Controversial');

    const updateButton = screen.getByRole('button', { name: /update style/i });
    await user.click(updateButton);

    await waitFor(() => {
      expect(screen.getByText('Super Controversial')).toBeInTheDocument();
      expect(screen.queryByText(/^Controversial$/)).not.toBeInTheDocument();
    });
  });

  it('deletes a style preset when confirmed', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    const { container } = render(<StylesPage />);

    const deleteButtons = container.querySelectorAll('button[title="Delete"]');
    const initialPresetsCount = deleteButtons.length;

    await user.click(deleteButtons[0]);

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this style preset?');

    await waitFor(() => {
      const remainingDeleteButtons = container.querySelectorAll('button[title="Delete"]');
      expect(remainingDeleteButtons).toHaveLength(initialPresetsCount - 1);
    });

    confirmSpy.mockRestore();
  });

  it('does not delete preset when cancelled', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
    const { container } = render(<StylesPage />);

    const deleteButtons = container.querySelectorAll('button[title="Delete"]');
    const initialPresetsCount = deleteButtons.length;

    await user.click(deleteButtons[0]);

    expect(confirmSpy).toHaveBeenCalled();
    expect(container.querySelectorAll('button[title="Delete"]')).toHaveLength(initialPresetsCount);

    confirmSpy.mockRestore();
  });

  it('resets to default presets when confirmed', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    // Add custom preset first
    const customPresets = [
      { id: '99', name: 'Custom Style', tone: 'unique', length: 'medium', useEmojis: true, description: 'Test' },
    ];
    localStorage.setItem('stylePresets', JSON.stringify(customPresets));

    render(<StylesPage />);

    expect(screen.getByText('Custom Style')).toBeInTheDocument();

    const resetButton = screen.getByRole('button', { name: /↺ reset to defaults/i });
    await user.click(resetButton);

    expect(confirmSpy).toHaveBeenCalledWith('Reset to default styles? This will delete all custom presets.');

    await waitFor(() => {
      expect(screen.getByText('Controversial')).toBeInTheDocument();
      expect(screen.queryByText('Custom Style')).not.toBeInTheDocument();
    });

    confirmSpy.mockRestore();
  });

  it('displays preset details correctly', () => {
    render(<StylesPage />);

    expect(screen.getAllByText(/tone: bold and provocative/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/length: medium/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/challenge conventional wisdom/i)).toBeInTheDocument();
  });

  it('displays emoji badge when preset uses emojis', () => {
    render(<StylesPage />);

    const emojiBadges = screen.getAllByText(/😊 emojis/i);
    // Sarcastic and Optimistic have emojis enabled
    expect(emojiBadges.length).toBeGreaterThan(0);
  });

  it('form requires all fields to be filled', async () => {
    const user = userEvent.setup();
    render(<StylesPage />);

    const addButton = screen.getByRole('button', { name: /\+ add custom style/i });
    await user.click(addButton);

    const createButton = screen.getByRole('button', { name: /create style/i });
    await user.click(createButton);

    // Form should not submit without required fields
    expect(screen.getByRole('heading', { name: /new style/i })).toBeInTheDocument();
  });

  it('resets form after successful creation', async () => {
    const user = userEvent.setup();
    render(<StylesPage />);

    const addButton = screen.getByRole('button', { name: /\+ add custom style/i });
    await user.click(addButton);

    await user.type(screen.getByLabelText(/style name/i), 'Test');
    await user.type(screen.getByLabelText(/^tone/i), 'test');
    await user.type(screen.getByLabelText(/description/i), 'test');

    const createButton = screen.getByRole('button', { name: /create style/i });
    await user.click(createButton);

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /new style/i })).not.toBeInTheDocument();
    });
  });

  it('populates form with preset data when editing', async () => {
    const user = userEvent.setup();
    const { container } = render(<StylesPage />);

    const editButtons = container.querySelectorAll('button[title="Edit"]');
    await user.click(editButtons[1]); // Edit "Sarcastic"

    expect(screen.getByLabelText(/style name/i)).toHaveValue('Sarcastic');
    expect(screen.getByLabelText(/^tone/i)).toHaveValue('witty and sharp');
    expect(screen.getByLabelText(/length/i)).toHaveValue('short');
    expect(screen.getByLabelText(/use emojis in hot takes/i)).toBeChecked();
    expect(screen.getByLabelText(/description/i)).toHaveValue('Humor with a bite');
  });
});
