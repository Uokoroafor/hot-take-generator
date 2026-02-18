import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SettingsPage from './SettingsPage';

describe('SettingsPage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    document.documentElement.classList.remove('dark-mode');
  });

  it('renders the page header', () => {
    render(<SettingsPage />);

    expect(screen.getByRole('heading', { name: /⚙️ settings/i })).toBeInTheDocument();
    expect(screen.getByText(/configure your hot take generator/i)).toBeInTheDocument();
  });

  it('renders current settings sections', () => {
    render(<SettingsPage />);

    expect(screen.getByRole('heading', { name: /appearance/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /data management/i })).toBeInTheDocument();
  });

  it('renders api configuration in non-production mode', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('heading', { name: /api configuration/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/api base url/i)).toBeInTheDocument();
  });

  it('loads dark mode setting from localStorage', () => {
    localStorage.setItem('darkMode', 'true');
    render(<SettingsPage />);

    const darkModeCheckbox = screen.getByLabelText(/🌙 enable dark mode/i) as HTMLInputElement;
    expect(darkModeCheckbox.checked).toBe(true);
  });

  it('loads API base URL from localStorage if set', () => {
    localStorage.setItem('apiBaseUrl', 'https://custom-api.com');
    render(<SettingsPage />);

    const apiInput = screen.getByLabelText(/api base url/i) as HTMLInputElement;
    expect(apiInput.value).toBe('https://custom-api.com');
  });

  it('saves apiBaseUrl override when changed', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);

    const apiInput = screen.getByLabelText(/api base url/i);
    const saveButton = screen.getByRole('button', { name: /save settings/i });

    await user.clear(apiInput);
    await user.type(apiInput, 'https://new-api.com');
    await user.click(saveButton);

    expect(localStorage.getItem('apiBaseUrl')).toBe('https://new-api.com');
  });

  it('removes apiBaseUrl override when saving default value', async () => {
    const user = userEvent.setup();
    localStorage.setItem('apiBaseUrl', 'https://custom-api.com');
    render(<SettingsPage />);

    const apiInput = screen.getByLabelText(/api base url/i);
    const saveButton = screen.getByRole('button', { name: /save settings/i });

    await user.clear(apiInput);
    await user.type(apiInput, 'http://localhost:8000');
    await user.click(saveButton);

    expect(localStorage.getItem('apiBaseUrl')).toBeNull();
  });

  it('shows success message after saving', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);

    await user.click(screen.getByRole('button', { name: /save settings/i }));
    expect(screen.getByRole('button', { name: /✓ saved!/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /save settings/i })).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('toggles dark mode immediately when checkbox is clicked', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);

    const darkModeCheckbox = screen.getByLabelText(/🌙 enable dark mode/i);
    await user.click(darkModeCheckbox);

    expect(localStorage.getItem('darkMode')).toBe('true');
  });

  it('resets to defaults when reset is confirmed', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    localStorage.setItem('apiBaseUrl', 'https://custom-api.com');
    render(<SettingsPage />);

    await user.click(screen.getByRole('button', { name: /reset to defaults/i }));
    expect(localStorage.getItem('apiBaseUrl')).toBeNull();
  });

  it('does not reset when reset is cancelled', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(false);
    localStorage.setItem('apiBaseUrl', 'https://custom-api.com');
    render(<SettingsPage />);

    await user.click(screen.getByRole('button', { name: /reset to defaults/i }));
    expect(localStorage.getItem('apiBaseUrl')).toBe('https://custom-api.com');
  });

  it('clears saved hot takes when confirmed', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.spyOn(window, 'alert').mockImplementation(() => {});
    localStorage.setItem('savedHotTakes', JSON.stringify([{ id: '1', hot_take: 'test' }]));
    render(<SettingsPage />);

    await user.click(screen.getByRole('button', { name: /^clear$/i }));
    expect(localStorage.getItem('savedHotTakes')).toBeNull();
  });

  it('renders data management copy for saved takes', () => {
    render(<SettingsPage />);
    expect(screen.getAllByText(/saved hot takes/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/your saved hot takes are stored locally/i)).toBeInTheDocument();
  });
});
