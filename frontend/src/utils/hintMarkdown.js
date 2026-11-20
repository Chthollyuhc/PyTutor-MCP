// Tiện ích thuần cho bảng Markdown trong gợi ý của Gia sư AI (Mức 3 có "bảng chạy tay" để trống).
// Không phụ thuộc React để kiểm thử bằng `node --test`.

const isTableLine = (line) => {
  const c = (line || '').trim();
  return c.length > 2 && c.startsWith('|') && c.endsWith('|');
};

// Gom các dòng liên tiếp bắt đầu và kết thúc bằng "|" thành một mục {table: [...dòng]}; dòng khác giữ nguyên {line}.
export function groupTableLines(lines) {
  const out = [];
  let rows = [];
  for (const line of lines) {
    if (isTableLine(line)) {
      rows.push(line.trim());
      continue;
    }
    if (rows.length) {
      out.push({ table: rows });
      rows = [];
    }
    out.push({ line });
  }
  if (rows.length) out.push({ table: rows });
  return out;
}

const isSeparatorRow = (cells) => cells.length > 0 && cells.every((c) => /^:?-{2,}:?$/.test(c.trim()));

// "| a | b |" -> {header: ['a','b'], body: [[...], ...]}. Dòng ngăn cách (---) bị bỏ; ô trống giữ chỗ.
export function parseTable(rows) {
  const split = (row) => row.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
  const cells = rows.map(split);
  const sepAt = cells.findIndex(isSeparatorRow);
  if (sepAt === 1) {
    return { header: cells[0], body: cells.slice(2) };
  }
  return { header: null, body: cells.filter((r) => !isSeparatorRow(r)) };
}
