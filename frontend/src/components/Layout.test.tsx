import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Layout from './Layout';

// Helper to render Layout with specific route
const renderWithRouter = (initialRoute = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Layout />
    </MemoryRouter>
  );
};

describe('Layout', () => {
  it('renders the navigation brand link', () => {
    renderWithRouter();

    const brandLink = screen.getByRole('link', { name: /🔥 hot take generator/i });
    expect(brandLink).toBeInTheDocument();
    expect(brandLink).toHaveAttribute('href', '/');
  });

  it('renders all navigation links', () => {
    renderWithRouter();

    expect(screen.getByRole('link', { name: /^generate$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^history$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^styles$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^agents$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^sources$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^settings$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^about$/i })).toBeInTheDocument();
  });

  it('has correct structure with nav and main sections', () => {
    const { container } = renderWithRouter();

    const nav = container.querySelector('.main-nav');
    const main = container.querySelector('.main-content');

    expect(nav).toBeInTheDocument();
    expect(main).toBeInTheDocument();
  });

  it('highlights active link for /generate route', () => {
    renderWithRouter('/generate');

    const generateLink = screen.getByRole('link', { name: /^generate$/i });
    expect(generateLink).toHaveClass('active');
  });

  it('highlights active link for /history route', () => {
    renderWithRouter('/history');

    const historyLink = screen.getByRole('link', { name: /^history$/i });
    expect(historyLink).toHaveClass('active');
  });

  it('highlights active link for /styles route', () => {
    renderWithRouter('/styles');

    const stylesLink = screen.getByRole('link', { name: /^styles$/i });
    expect(stylesLink).toHaveClass('active');
  });

  it('highlights active link for /agents route', () => {
    renderWithRouter('/agents');

    const agentsLink = screen.getByRole('link', { name: /^agents$/i });
    expect(agentsLink).toHaveClass('active');
  });

  it('highlights active link for /sources route', () => {
    renderWithRouter('/sources');

    const sourcesLink = screen.getByRole('link', { name: /^sources$/i });
    expect(sourcesLink).toHaveClass('active');
  });

  it('highlights active link for /settings route', () => {
    renderWithRouter('/settings');

    const settingsLink = screen.getByRole('link', { name: /^settings$/i });
    expect(settingsLink).toHaveClass('active');
  });

  it('highlights active link for /about route', () => {
    renderWithRouter('/about');

    const aboutLink = screen.getByRole('link', { name: /^about$/i });
    expect(aboutLink).toHaveClass('active');
  });

  it('highlights generate link for root route', () => {
    renderWithRouter('/');

    const generateLink = screen.getByRole('link', { name: /^generate$/i });
    expect(generateLink).toHaveClass('active');
  });

  it('only highlights one active link at a time', () => {
    renderWithRouter('/history');

    const links = screen.getAllByRole('link').filter(link =>
      ['generate', 'history', 'styles', 'agents', 'sources', 'settings', 'about']
        .some(name => link.textContent?.toLowerCase() === name)
    );

    const activeLinks = links.filter(link => link.classList.contains('active'));
    expect(activeLinks).toHaveLength(1);
    expect(activeLinks[0]).toHaveTextContent(/history/i);
  });

  it('all navigation links have correct href attributes', () => {
    renderWithRouter();

    expect(screen.getByRole('link', { name: /^generate$/i })).toHaveAttribute('href', '/generate');
    expect(screen.getByRole('link', { name: /^history$/i })).toHaveAttribute('href', '/history');
    expect(screen.getByRole('link', { name: /^styles$/i })).toHaveAttribute('href', '/styles');
    expect(screen.getByRole('link', { name: /^agents$/i })).toHaveAttribute('href', '/agents');
    expect(screen.getByRole('link', { name: /^sources$/i })).toHaveAttribute('href', '/sources');
    expect(screen.getByRole('link', { name: /^settings$/i })).toHaveAttribute('href', '/settings');
    expect(screen.getByRole('link', { name: /^about$/i })).toHaveAttribute('href', '/about');
  });
});
