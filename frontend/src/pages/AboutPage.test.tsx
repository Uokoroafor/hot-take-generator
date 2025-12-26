import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import AboutPage from './AboutPage';

describe('AboutPage', () => {
  it('renders the page header', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /ℹ️ about/i })).toBeInTheDocument();
    expect(screen.getByText(/^hot take generator$/i)).toBeInTheDocument();
  });

  it('renders the "What is this?" section', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /what is this\?/i })).toBeInTheDocument();
    expect(screen.getByText(/the hot take generator is a full-stack application/i)).toBeInTheDocument();
  });

  it('mentions AI and hot takes in description', () => {
    render(<AboutPage />);

    expect(screen.getByText(/spicy, controversial, and thought-provoking opinions/i)).toBeInTheDocument();
  });

  it('references The Arsenal Opinion Podcast inspiration', () => {
    render(<AboutPage />);

    const link = screen.getByRole('link', { name: /the arsenal opinion podcast/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://www.le-grove.co.uk/s/the-arsenal-opinion-podcast');
  });

  it('renders the Features section', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /^features$/i })).toBeInTheDocument();
  });

  it('lists all key features', () => {
    render(<AboutPage />);

    expect(screen.getByText(/multiple ai agents/i)).toBeInTheDocument();
    expect(screen.getByText(/various hot take styles/i)).toBeInTheDocument();
    expect(screen.getByText(/web search integration/i)).toBeInTheDocument();
    expect(screen.getByText(/news search/i)).toBeInTheDocument();
    expect(screen.getByText(/dark mode support/i)).toBeInTheDocument();
    expect(screen.getByText(/save and manage your favorite hot takes/i)).toBeInTheDocument();
    expect(screen.getByText(/customizable style presets/i)).toBeInTheDocument();
    expect(screen.getByText(/agent performance monitoring/i)).toBeInTheDocument();
  });

  it('renders the Tech Stack section', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /^tech stack$/i })).toBeInTheDocument();
  });

  it('lists frontend technologies', () => {
    render(<AboutPage />);

    expect(screen.getByText(/react 19/i)).toBeInTheDocument();
    expect(screen.getByText(/typescript/i)).toBeInTheDocument();
    expect(screen.getByText(/vite/i)).toBeInTheDocument();
    expect(screen.getByText(/react router/i)).toBeInTheDocument();
  });

  it('lists backend technologies', () => {
    render(<AboutPage />);

    expect(screen.getByText(/fastapi/i)).toBeInTheDocument();
    expect(screen.getByText(/openai api/i)).toBeInTheDocument();
    expect(screen.getByText(/anthropic api/i)).toBeInTheDocument();
    expect(screen.getByText(/web search apis/i)).toBeInTheDocument();
  });

  it('renders the Open Source section', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /^open source$/i })).toBeInTheDocument();
    expect(screen.getByText(/this project is open source and available on github/i)).toBeInTheDocument();
  });

  it('has GitHub repository link', () => {
    render(<AboutPage />);

    const githubLink = screen.getByRole('link', { name: /📦 view on github/i });
    expect(githubLink).toBeInTheDocument();
    expect(githubLink).toHaveAttribute('href', 'https://github.com/Uokoroafor/hot-take-generator');
    expect(githubLink).toHaveAttribute('target', '_blank');
    expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('has GitHub issues link', () => {
    render(<AboutPage />);

    const issuesLink = screen.getByRole('link', { name: /🐛 report an issue/i });
    expect(issuesLink).toBeInTheDocument();
    expect(issuesLink).toHaveAttribute('href', 'https://github.com/Uokoroafor/hot-take-generator/issues');
    expect(issuesLink).toHaveAttribute('target', '_blank');
    expect(issuesLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('renders the Credits section', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /^credits$/i })).toBeInTheDocument();
    expect(screen.getByText(/created by/i)).toBeInTheDocument();
    expect(screen.getByText(/ugochukwu okoroafor/i)).toBeInTheDocument();
  });

  it('credits The Arsenal Opinion Podcast in credits section', () => {
    render(<AboutPage />);

    const creditsSection = screen.getByRole('heading', { name: /^credits$/i }).parentElement;
    expect(creditsSection).toHaveTextContent(/inspired by the arsenal opinion podcast/i);
  });

  it('renders the License section', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /^license$/i })).toBeInTheDocument();
    expect(screen.getByText(/mit license/i)).toBeInTheDocument();
    expect(screen.getByText(/free to use, modify, and distribute/i)).toBeInTheDocument();
  });

  it('has Frontend and Backend subsections in Tech Stack', () => {
    render(<AboutPage />);

    expect(screen.getByRole('heading', { name: /^frontend$/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /^backend$/i })).toBeInTheDocument();
  });

  it('displays feature list with proper icons', () => {
    render(<AboutPage />);

    const featuresList = screen.getByRole('heading', { name: /^features$/i }).nextElementSibling;
    expect(featuresList).toHaveClass('features-list');
  });

  it('GitHub links open in new tab with security attributes', () => {
    render(<AboutPage />);

    const githubLinks = [
      screen.getByRole('link', { name: /📦 view on github/i }),
      screen.getByRole('link', { name: /🐛 report an issue/i }),
    ];

    githubLinks.forEach(link => {
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  it('renders all main sections', () => {
    render(<AboutPage />);

    const sections = [
      /what is this\?/i,
      /^features$/i,
      /^tech stack$/i,
      /^open source$/i,
      /^credits$/i,
      /^license$/i,
    ];

    sections.forEach(sectionName => {
      expect(screen.getByRole('heading', { name: sectionName })).toBeInTheDocument();
    });
  });

  it('mentions both GPT and Claude models', () => {
    render(<AboutPage />);

    expect(screen.getByText(/openai gpt & anthropic claude/i)).toBeInTheDocument();
  });

  it('describes the inspiration correctly', () => {
    render(<AboutPage />);

    const hottestOfTakesText = screen.getAllByText(/hottest of takes/i);
    expect(hottestOfTakesText.length).toBeGreaterThan(0);
    expect(screen.getByText(/bold, entertaining commentary/i)).toBeInTheDocument();
  });

  it('mentions current events and context-aware takes', () => {
    render(<AboutPage />);

    expect(screen.getByText(/timely, context-aware takes/i)).toBeInTheDocument();
    expect(screen.getByText(/current events/i)).toBeInTheDocument();
  });

  it('has proper semantic HTML structure', () => {
    const { container } = render(<AboutPage />);

    expect(container.querySelector('.page-container')).toBeInTheDocument();
    expect(container.querySelector('.page-header')).toBeInTheDocument();
    expect(container.querySelector('.about-content')).toBeInTheDocument();
  });
});
