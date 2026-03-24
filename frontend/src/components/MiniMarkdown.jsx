/**
 * Lightweight markdown renderer for chat bubbles.
 * Handles: **bold**, *italic*, `code`, and line breaks.
 * No external dependencies needed.
 */
import React from 'react';

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function parseLine(line) {
  // Code spans
  line = line.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold
  line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic
  line = line.replace(/\*(.+?)\*/g, '<em>$1</em>');
  return line;
}

export default function MiniMarkdown({ content = '' }) {
  const lines = content.split('\n');
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const raw = lines[i];
    const trimmed = raw.trim();

    if (!trimmed) {
      // blank line → spacing
      elements.push(<div key={i} style={{ height: '0.4rem' }} />);
      i++;
    } else if (/^\d+\.\s/.test(trimmed)) {
      // Numbered list
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^\d+\.\s/, ''));
        i++;
      }
      elements.push(
        <ol key={`ol-${i}`} className="md-ol">
          {items.map((it, j) => (
            <li key={j} dangerouslySetInnerHTML={{ __html: parseLine(it) }} />
          ))}
        </ol>
      );
    } else if (/^[-*•]\s/.test(trimmed)) {
      // Bullet list
      const items = [];
      while (i < lines.length && /^[-*•]\s/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^[-*•]\s/, ''));
        i++;
      }
      elements.push(
        <ul key={`ul-${i}`} className="md-ul">
          {items.map((it, j) => (
            <li key={j} dangerouslySetInnerHTML={{ __html: parseLine(it) }} />
          ))}
        </ul>
      );
    } else if (/^#{1,3}\s/.test(trimmed)) {
      // Heading
      const level = trimmed.match(/^(#+)/)[1].length;
      const text = trimmed.replace(/^#+\s/, '');
      const Tag = `h${Math.min(level, 3)}`;
      elements.push(
        <Tag key={i} className={`md-h${level}`} dangerouslySetInnerHTML={{ __html: parseLine(text) }} />
      );
      i++;
    } else {
      elements.push(
        <p key={i} className="md-p" dangerouslySetInnerHTML={{ __html: parseLine(trimmed) }} />
      );
      i++;
    }
  }

  return <div className="mini-markdown">{elements}</div>;
}
