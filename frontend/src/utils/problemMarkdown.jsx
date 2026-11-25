import React from 'react';

// Hiển thị Markdown nhẹ cho đề bài: `code`, **đậm**, *nghiêng*, $công thức$ (LaTeX đơn giản → ký hiệu Unicode).

const SUP = { '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '+': '⁺', '-': '⁻', n: 'ⁿ' };
const SUB = { '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉', '+': '₊', '-': '₋' };

const SYMBOLS = {
  '\\le': '≤', '\\leq': '≤', '\\ge': '≥', '\\geq': '≥', '\\ne': '≠', '\\neq': '≠',
  '\\dots': '…', '\\ldots': '…', '\\cdots': '…', '\\times': '×', '\\cdot': '·',
  '\\pm': '±', '\\approx': '≈', '\\to': '→', '\\rightarrow': '→', '\\infty': '∞',
  '\\sum': 'Σ', '\\pi': 'π', '\\div': '÷', '\\in': '∈', '\\%': '%',
};

function mapScript(str, table) {
  const out = [...str].map((ch) => table[ch]);
  return out.every(Boolean) ? out.join('') : null;
}

export function latexToText(src) {
  let s = src.trim();
  s = s.replace(/\\(?:text|mathrm|mathbf|operatorname)\{([^}]*)\}/g, '$1');
  s = s.replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, '($1)/($2)');
  s = s.replace(/\\sqrt\{([^}]*)\}/g, '√($1)');
  s = s.replace(/\\[a-zA-Z%]+/g, (m) => SYMBOLS[m] ?? m.slice(1));
  s = s.replace(/\^\{([^}]*)\}|\^(\w)/g, (_, a, b) => {
    const body = a ?? b;
    return mapScript(body, SUP) ?? `^${body.length > 1 ? `(${body})` : body}`;
  });
  s = s.replace(/_\{([^}]*)\}|_(\w)/g, (_, a, b) => {
    const body = a ?? b;
    return mapScript(body, SUB) ?? `_${body}`;
  });
  return s.replace(/\s+/g, ' ');
}

const INLINE = /(`[^`]+`)|(\$\$[^$]+\$\$)|(\$[^$\n]+\$)|(\*\*[^*]+\*\*)|(\*[^*\s][^*]*\*)/g;

export function renderInline(text, keyPrefix = 'in') {
  const nodes = [];
  let last = 0;
  let m;
  let k = 0;
  INLINE.lastIndex = 0;
  while ((m = INLINE.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    const tok = m[0];
    const key = `${keyPrefix}-${k++}`;
    if (m[1]) {
      nodes.push(<code key={key} className="rounded bg-surface-raised px-1 py-0.5 font-mono text-[0.85em] text-primary-strong">{tok.slice(1, -1)}</code>);
    } else if (m[2]) {
      nodes.push(<em key={key} className="font-serif">{latexToText(tok.slice(2, -2))}</em>);
    } else if (m[3]) {
      nodes.push(<em key={key} className="font-serif">{latexToText(tok.slice(1, -1))}</em>);
    } else if (m[4]) {
      nodes.push(<strong key={key} className="font-semibold">{renderInline(tok.slice(2, -2), key)}</strong>);
    } else {
      nodes.push(<em key={key}>{tok.slice(1, -1)}</em>);
    }
    last = m.index + tok.length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

function Table({ rows, id }) {
  return (
    <div key={id} className="my-2.5 overflow-x-auto rounded border border-primary-line">
      <table className="min-w-full text-xs font-mono text-left">
        <thead className="border-b border-primary-line bg-primary-soft text-primary-strong">
          <tr>
            {rows[0].map((th, i) => (
              <th key={i} className="px-3 py-1.5 font-semibold">{renderInline(th, `th${i}`)}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-surface">
          {rows.slice(1).map((row, r) => (
            <tr key={r}>
              {row.map((cell, c) => (
                <td key={c} className="px-3 py-1.5 text-foreground">{renderInline(cell, `td${r}-${c}`)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function renderFormattedContent(text) {
  if (!text) return null;
  const lines = text.split('\n');
  const elements = [];
  let tableRows = [];
  let inCode = false;
  let codeLines = [];

  const flushTable = (id) => {
    if (tableRows.length > 0) elements.push(<Table key={`tbl-${id}`} id={id} rows={tableRows} />);
    tableRows = [];
  };

  lines.forEach((line, i) => {
    const trimmed = line.trim();

    if (trimmed.startsWith('```')) {
      if (inCode) {
        elements.push(
          <pre key={`code-${i}`} className="overflow-x-auto rounded-xl border border-border bg-surface-raised p-3 font-mono text-xs leading-5">{codeLines.join('\n')}</pre>
        );
        codeLines = [];
      }
      inCode = !inCode;
      return;
    }
    if (inCode) {
      codeLines.push(line);
      return;
    }

    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      if (!/^\|[\s:|-]+\|$/.test(trimmed)) {
        tableRows.push(trimmed.split('|').slice(1, -1).map((c) => c.trim()));
      }
      return;
    }
    flushTable(i);

    const heading = trimmed.match(/^#{1,6}\s+(.*)$/);
    const bullet = trimmed.match(/^[-*]\s+(.*)$/);
    const ordered = trimmed.match(/^(\d+)[.)]\s+(.*)$/);

    if (heading) {
      elements.push(
        <h3 key={i} className="mb-1 mt-4 text-base font-bold text-primary-strong">{renderInline(heading[1], `h${i}`)}</h3>
      );
    } else if (bullet) {
      elements.push(
        <div key={i} className="ml-1 flex items-start gap-2 text-sm leading-6 text-foreground">
          <span aria-hidden="true" className="text-muted">•</span>
          <span>{renderInline(bullet[1], `b${i}`)}</span>
        </div>
      );
    } else if (ordered) {
      elements.push(
        <div key={i} className="ml-1 flex items-start gap-2 text-sm leading-6 text-foreground">
          <span aria-hidden="true" className="min-w-4 text-muted">{ordered[1]}.</span>
          <span>{renderInline(ordered[2], `o${i}`)}</span>
        </div>
      );
    } else if (/^\$\$[^$]+\$\$$/.test(trimmed)) {
      elements.push(
        <p key={i} className="my-1 text-center font-serif text-base italic text-foreground">{latexToText(trimmed.slice(2, -2))}</p>
      );
    } else if (trimmed !== '') {
      elements.push(
        <p key={i} className="text-sm leading-6 text-foreground">{renderInline(trimmed, `p${i}`)}</p>
      );
    }
  });

  flushTable('end');
  return elements;
}
