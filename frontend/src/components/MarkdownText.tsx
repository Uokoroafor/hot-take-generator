import type { ReactNode } from 'react';

interface MarkdownTextProps {
  text: string;
  className?: string;
}

const INLINE_PATTERN =
  /(\*\*([^*]+)\*\*|__([^_]+)__|\*([^*]+)\*|_([^_]+)_|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\))/g;

const isAllowedUrl = (url: string): boolean => {
  const trimmed = url.trim();
  if (!trimmed) return false;
  if (trimmed.startsWith('/')) return true;
  try {
    const parsed = new URL(trimmed, 'https://example.com');
    return (
      parsed.protocol === 'http:' ||
      parsed.protocol === 'https:' ||
      parsed.protocol === 'mailto:'
    );
  } catch {
    return false;
  }
};

const renderInline = (text: string, keyPrefix: string): ReactNode[] => {
  const nodes: ReactNode[] = [];
  let cursor = 0;
  let matchIndex = 0;
  let match: RegExpExecArray | null;

  INLINE_PATTERN.lastIndex = 0;
  match = INLINE_PATTERN.exec(text);
  while (match !== null) {
    if (match.index > cursor) {
      nodes.push(text.slice(cursor, match.index));
    }

    const fullMatch = match[0];
    const strongA = match[2];
    const strongB = match[3];
    const emA = match[4];
    const emB = match[5];
    const code = match[6];
    const linkText = match[7];
    const linkUrl = match[8];
    const key = `${keyPrefix}-inline-${matchIndex++}`;

    if (strongA || strongB) {
      nodes.push(<strong key={key}>{strongA || strongB}</strong>);
    } else if (emA || emB) {
      nodes.push(<em key={key}>{emA || emB}</em>);
    } else if (code) {
      nodes.push(<code key={key}>{code}</code>);
    } else if (linkText && linkUrl && isAllowedUrl(linkUrl)) {
      nodes.push(
        <a key={key} href={linkUrl} target="_blank" rel="noopener noreferrer">
          {linkText}
        </a>
      );
    } else {
      nodes.push(fullMatch);
    }

    cursor = match.index + fullMatch.length;
    match = INLINE_PATTERN.exec(text);
  }

  if (cursor < text.length) {
    nodes.push(text.slice(cursor));
  }

  return nodes;
};

const MarkdownText = ({ text, className }: MarkdownTextProps) => {
  const lines = text.split('\n');
  const blocks: ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const current = lines[i];
    const trimmed = current.trim();

    if (!trimmed) {
      i += 1;
      continue;
    }

    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const headingText = heading[2];
      const headingKey = `h-${i}`;
      if (level === 1) blocks.push(<h1 key={headingKey}>{renderInline(headingText, headingKey)}</h1>);
      else if (level === 2)
        blocks.push(<h2 key={headingKey}>{renderInline(headingText, headingKey)}</h2>);
      else if (level === 3)
        blocks.push(<h3 key={headingKey}>{renderInline(headingText, headingKey)}</h3>);
      else if (level === 4)
        blocks.push(<h4 key={headingKey}>{renderInline(headingText, headingKey)}</h4>);
      else if (level === 5)
        blocks.push(<h5 key={headingKey}>{renderInline(headingText, headingKey)}</h5>);
      else blocks.push(<h6 key={headingKey}>{renderInline(headingText, headingKey)}</h6>);
      i += 1;
      continue;
    }

    if (/^[-*+]\s+/.test(trimmed)) {
      const items: string[] = [];
      let j = i;
      while (j < lines.length) {
        const item = lines[j].trim().match(/^[-*+]\s+(.+)$/);
        if (!item) break;
        items.push(item[1]);
        j += 1;
      }
      blocks.push(
        <ul key={`ul-${i}`}>
          {items.map((item, idx) => (
            <li key={`ul-${i}-${idx}`}>{renderInline(item, `ul-${i}-${idx}`)}</li>
          ))}
        </ul>
      );
      i = j;
      continue;
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      const items: string[] = [];
      let j = i;
      while (j < lines.length) {
        const item = lines[j].trim().match(/^\d+\.\s+(.+)$/);
        if (!item) break;
        items.push(item[1]);
        j += 1;
      }
      blocks.push(
        <ol key={`ol-${i}`}>
          {items.map((item, idx) => (
            <li key={`ol-${i}-${idx}`}>{renderInline(item, `ol-${i}-${idx}`)}</li>
          ))}
        </ol>
      );
      i = j;
      continue;
    }

    if (trimmed.startsWith('>')) {
      const quoteLines: string[] = [];
      let j = i;
      while (j < lines.length) {
        const line = lines[j].trim();
        if (!line.startsWith('>')) break;
        quoteLines.push(line.replace(/^>\s?/, ''));
        j += 1;
      }
      blocks.push(
        <blockquote key={`q-${i}`}>
          {quoteLines.map((line, idx) => (
            <p key={`q-${i}-${idx}`}>{renderInline(line, `q-${i}-${idx}`)}</p>
          ))}
        </blockquote>
      );
      i = j;
      continue;
    }

    const paragraphLines: string[] = [];
    let j = i;
    while (j < lines.length) {
      const line = lines[j];
      const plain = line.trim();
      if (
        !plain ||
        /^(#{1,6})\s+/.test(plain) ||
        /^[-*+]\s+/.test(plain) ||
        /^\d+\.\s+/.test(plain) ||
        plain.startsWith('>')
      ) {
        break;
      }
      paragraphLines.push(plain);
      j += 1;
    }

    const paragraphText = paragraphLines.join(' ');
    blocks.push(<p key={`p-${i}`}>{renderInline(paragraphText, `p-${i}`)}</p>);
    i = j;
  }

  return <div className={className}>{blocks}</div>;
};

export default MarkdownText;
