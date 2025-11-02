import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders the main heading', () => {
    render(<App />);

    const heading = screen.getByRole('heading', { name: /hot take generator/i });
    expect(heading).toBeInTheDocument();
  });

  it('renders the subtitle description', () => {
    render(<App />);

    expect(
      screen.getByText(/generate spicy opinions on any topic with ai agents/i)
    ).toBeInTheDocument();
  });

  it('renders the HotTakeGenerator component', () => {
    render(<App />);

    // Check that the form from HotTakeGenerator is present
    expect(screen.getByLabelText(/topic/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/style/i)).toBeInTheDocument();
  });

  it('has correct structure with header and main sections', () => {
    const { container } = render(<App />);

    const header = container.querySelector('.App-header');
    const main = container.querySelector('main');

    expect(header).toBeInTheDocument();
    expect(main).toBeInTheDocument();
  });
});
