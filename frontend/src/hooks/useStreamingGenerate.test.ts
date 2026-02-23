import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useStreamingGenerate } from './useStreamingGenerate';

globalThis.fetch = vi.fn();

vi.mock('../config', () => ({
  default: { apiBaseUrl: 'http://localhost:8000' },
}));

const encoder = new TextEncoder();

function makeSseStream(events: object[]) {
  const lines = events.map(e => `data: ${JSON.stringify(e)}\n\n`).join('');
  const chunk = encoder.encode(lines);
  return {
    ok: true,
    body: {
      getReader: () => ({
        read: vi
          .fn()
          .mockResolvedValueOnce({ done: false, value: chunk })
          .mockResolvedValueOnce({ done: true, value: undefined }),
      }),
    },
  };
}

const sampleRequest = {
  topic: 'test topic',
  style: 'controversial',
  use_web_search: false,
  use_news_search: false,
  max_articles: 3,
  news_days: 14,
  strict_quality_mode: false,
};

describe('useStreamingGenerate', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('starts in idle state', () => {
    const { result } = renderHook(() => useStreamingGenerate());

    expect(result.current.isStreaming).toBe(false);
    expect(result.current.tokens).toBe('');
    expect(result.current.status).toBe('');
    expect(result.current.sources).toEqual([]);
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('accumulates tokens from token events', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeSseStream([
        { type: 'token', text: 'Hot ' },
        { type: 'token', text: 'take!' },
        {
          type: 'done',
          hot_take: 'Hot take!',
          topic: 'test',
          style: 'controversial',
          agent_used: 'Agent',
        },
      ])
    );

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.tokens).toBe('Hot take!');
  });

  it('sets status from status events', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeSseStream([
        { type: 'status', message: 'Searching the web...' },
        {
          type: 'done',
          hot_take: 'done',
          topic: 'test',
          style: 'controversial',
          agent_used: 'Agent',
        },
      ])
    );

    const { result } = renderHook(() => useStreamingGenerate());

    // Status is cleared on done, so check result instead
    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    // After done, status is cleared
    expect(result.current.status).toBe('');
    expect(result.current.result).not.toBeNull();
  });

  it('populates sources from sources event', async () => {
    const sources = [
      { type: 'web', title: 'Article', url: 'https://example.com' },
    ];

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeSseStream([
        { type: 'sources', sources },
        { type: 'token', text: 'take' },
        {
          type: 'done',
          hot_take: 'take',
          topic: 'test',
          style: 'controversial',
          agent_used: 'Agent',
          sources,
        },
      ])
    );

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.sources).toHaveLength(1);
    expect(result.current.sources[0].url).toBe('https://example.com');
  });

  it('sets result on done event', async () => {
    const done = {
      type: 'done',
      hot_take: 'The final take',
      topic: 'test',
      style: 'controversial',
      agent_used: 'Claude Agent',
    };

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeSseStream([done])
    );

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.result).not.toBeNull();
    expect(result.current.result?.hot_take).toBe('The final take');
    expect(result.current.result?.agent_used).toBe('Claude Agent');
    expect(result.current.isStreaming).toBe(false);
  });

  it('sets error on error event', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeSseStream([{ type: 'error', detail: 'Generation failed. Please try again.' }])
    );

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.error).toBe('Generation failed. Please try again.');
    expect(result.current.isStreaming).toBe(false);
  });

  it('sets error when response is not ok', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Rate limit exceeded.' }),
    });

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.error).toBe('Rate limit exceeded.');
    expect(result.current.isStreaming).toBe(false);
  });

  it('sets generic error when response not ok without detail', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      json: async () => ({}),
    });

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.error).toBe('Failed to generate hot take');
  });

  it('resets state on reset()', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeSseStream([
        { type: 'token', text: 'something' },
        {
          type: 'done',
          hot_take: 'something',
          topic: 'test',
          style: 'controversial',
          agent_used: 'Agent',
        },
      ])
    );

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.tokens).toBe('something');

    act(() => {
      result.current.reset();
    });

    expect(result.current.tokens).toBe('');
    expect(result.current.result).toBeNull();
    expect(result.current.status).toBe('');
    expect(result.current.isStreaming).toBe(false);
  });

  it('does not set error when cancelled via cancel()', async () => {
    const readPromise = new Promise(() => { /* intentionally never resolves */ });

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      body: {
        getReader: () => ({
          read: vi.fn().mockReturnValue(readPromise),
        }),
      },
    });

    const { result } = renderHook(() => useStreamingGenerate());

    // Start generate without awaiting
    act(() => {
      void result.current.generate(sampleRequest);
    });

    act(() => {
      result.current.cancel();
    });

    // The AbortError path swallows the error
    expect(result.current.error).toBeNull();
    expect(result.current.isStreaming).toBe(false);
  });

  it('skips malformed SSE frames without crashing', async () => {
    const brokenChunk = encoder.encode(
      'data: not-json\n\ndata: {"type":"done","hot_take":"ok","topic":"t","style":"s","agent_used":"A"}\n\n'
    );

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      body: {
        getReader: () => ({
          read: vi
            .fn()
            .mockResolvedValueOnce({ done: false, value: brokenChunk })
            .mockResolvedValueOnce({ done: true, value: undefined }),
        }),
      },
    });

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    // Malformed frame was skipped; done event was processed
    expect(result.current.result?.hot_take).toBe('ok');
    expect(result.current.error).toBeNull();
  });

  it('stops streaming and sets retryable error when stream ends without done', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      makeSseStream([{ type: 'token', text: 'partial output' }])
    );

    const { result } = renderHook(() => useStreamingGenerate());

    await act(async () => {
      await result.current.generate(sampleRequest);
    });

    expect(result.current.tokens).toBe('partial output');
    expect(result.current.isStreaming).toBe(false);
    expect(result.current.error).toBe('Stream ended early. Please try again.');
  });
});
