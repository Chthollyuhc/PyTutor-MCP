import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const file = join(dirname(fileURLToPath(import.meta.url)), '..', 'components', 'journey', 'ConceptMap.jsx');
const BANNED = ['mcp', 'heuristic', 'bkt', 'xếp hạng', 'trung vị', 'mắc kẹt', 'đạt độc lập', 'thất bại'];

test('ConceptMap không chứa từ cấm, có ghi chú ước lượng tạm thời', () => {
  const text = readFileSync(file, 'utf8');
  const low = text.toLowerCase();
  for (const w of BANNED) assert.ok(!low.includes(w), `ConceptMap chứa "${w}"`);
  assert.ok(text.includes('ước lượng tạm thời, chưa hiệu chuẩn'));
  assert.ok(text.includes('explanation_vi') && text.includes('common_error_vi'));
});
