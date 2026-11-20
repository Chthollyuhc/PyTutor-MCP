import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const components = join(here, '..', 'components');
const FILES = [
  ...readdirSync(join(components, 'plain')).filter((f) => f.endsWith('.jsx')).map((f) => join(components, 'plain', f)),
  join(components, 'StudentProfileModal.jsx'),
];
const BANNED = ['khái niệm', 'trạng thái', 'bằng chứng', 'quy ước', 'hiệu chuẩn', 'trung vị', 'chỉ số tự làm',
  'nhóm quá trình', 'mắc kẹt', 'đạt độc lập', 'thử–sửa', 'lượt', 'heuristic', 'xếp hạng'];

test('các màn lời thường không chứa từ chuyên môn', () => {
  for (const file of FILES) {
    const text = readFileSync(file, 'utf8').toLowerCase();
    for (const word of BANNED) assert.ok(!text.includes(word), `${file} chứa "${word}"`);
  }
});
