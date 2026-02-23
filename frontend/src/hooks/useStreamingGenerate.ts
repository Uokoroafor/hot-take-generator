import { useState, useCallback, useRef } from 'react';
import config from '../config';

export interface SourceRecord {
  type: 'web' | 'news';
  title: string;
  url: string;
  snippet?: string;
  source?: string;
  published?: string;
}

export interface StreamResult {
  hot_take: string;
  topic: string;
  style: string;
  agent_used: string;
  web_search_used?: boolean;
  news_context?: string;
  sources?: SourceRecord[];
}

export interface GenerateRequest {
  topic: string;
  style: string;
  agent_type?: string;
  use_web_search: boolean;
  use_news_search: boolean;
  max_articles: number;
  web_search_provider?: string;
  news_days: number;
  strict_quality_mode: boolean;
}

export interface StreamState {
  status: string;
  tokens: string;
  sources: SourceRecord[];
  result: StreamResult | null;
  isStreaming: boolean;
  error: string | null;
}

const INITIAL_STATE: StreamState = {
  status: '',
  tokens: '',
  sources: [],
  result: null,
  isStreaming: false,
  error: null,
};

export type GenerateOutcome =
  | { ok: true; result: StreamResult | null }
  | { ok: false; error: string };

export function useStreamingGenerate() {
  const [state, setState] = useState<StreamState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);

  const generate = useCallback(async (request: GenerateRequest): Promise<GenerateOutcome> => {
    // Cancel any in-flight request
    if (abortRef.current) {
      abortRef.current.abort();
    }

    const controller = new AbortController();
    abortRef.current = controller;

    setState({ ...INITIAL_STATE, isStreaming: true });

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/generate/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let message = 'Failed to generate hot take';
        try {
          const err = await response.json();
          if (typeof err.detail === 'string' && err.detail.trim()) {
            message = err.detail;
          }
        } catch {
          // keep generic message
        }
        throw new Error(message);
      }

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let receivedDone = false;
      let finalResult: StreamResult | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Split on newlines; keep the last (potentially incomplete) line in the buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6);
          if (!jsonStr.trim()) continue;

          let event: { type: string; [key: string]: unknown };
          try {
            event = JSON.parse(jsonStr);
          } catch {
            continue; // skip malformed frames
          }

          if (event.type === 'status') {
            setState(prev => ({ ...prev, status: event.message as string }));
          } else if (event.type === 'sources') {
            setState(prev => ({ ...prev, sources: event.sources as SourceRecord[] }));
          } else if (event.type === 'token') {
            setState(prev => ({ ...prev, tokens: prev.tokens + (event.text as string) }));
          } else if (event.type === 'done') {
            receivedDone = true;
            finalResult = event as unknown as StreamResult;
            setState(prev => ({
              ...prev,
              result: finalResult,
              status: '',
              isStreaming: false,
            }));
          } else if (event.type === 'error') {
            throw new Error(event.detail as string);
          }
        }
      }

      // Clean EOF without a terminal "done" frame: stop spinner and report a retryable error.
      if (!receivedDone) {
        const message = 'Stream ended early. Please try again.';
        setState(prev => ({ ...prev, error: message, isStreaming: false, status: '' }));
        return { ok: false, error: message };
      }

      return { ok: true, result: finalResult };
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return { ok: false, error: 'Request cancelled' }; // intentional cancel
      }
      const message =
        err instanceof Error ? err.message : 'An error occurred';
      setState(prev => ({ ...prev, error: message, isStreaming: false, status: '' }));
      return { ok: false, error: message };
    }
  }, []);

  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setState(prev => ({ ...prev, isStreaming: false, status: '' }));
  }, []);

  const reset = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setState(INITIAL_STATE);
  }, []);

  return { ...state, generate, cancel, reset };
}
