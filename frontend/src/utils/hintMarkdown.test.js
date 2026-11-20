import test from 'node:test';
import assert from 'node:assert/strict';
import { groupTableLines, parseTable } from './hintMarkdown.js';

const TABLE = [
  '| Bước | `n` | `tong` | Đã in |',
  '|---|---|---|---|',
  '| Sau khi đọc dữ liệu |   |   |   |',
  '| Kết quả cuối |   |   |   |',
];

test('groupTableLines gom dòng bảng liên tiếp và giữ nguyên dòng thường', () => {
  const items = groupTableLines(['Chạy tay với đầu vào `1`:', ...TABLE, 'Dòng sau bảng']);
  assert.equal(items.length, 3);
  assert.equal(items[0].line, 'Chạy tay với đầu vào `1`:');
  assert.equal(items[1].table.length, 4);
  assert.equal(items[2].line, 'Dòng sau bảng');
});

test('groupTableLines không coi dòng chỉ có một dấu | hoặc văn bản có | giữa dòng là bảng', () => {
  const items = groupTableLines(['|', 'a | b', 'x |', '| y']);
  assert.ok(items.every((i) => i.line !== undefined));
});

test('parseTable tách tiêu đề, bỏ dòng ngăn cách và giữ ô trống', () => {
  const t = parseTable(TABLE);
  assert.deepEqual(t.header, ['Bước', '`n`', '`tong`', 'Đã in']);
  assert.equal(t.body.length, 2);
  assert.deepEqual(t.body[0], ['Sau khi đọc dữ liệu', '', '', '']);
});

test('parseTable xử lý bảng không có dòng ngăn cách', () => {
  const t = parseTable(['| a | b |', '| c | d |']);
  assert.equal(t.header, null);
  assert.equal(t.body.length, 2);
});

test('nhóm hai bảng cách nhau bằng dòng thường thành hai mục', () => {
  const items = groupTableLines(['| a |', 'giữa', '| b |']);
  assert.equal(items.filter((i) => i.table).length, 2);
});
