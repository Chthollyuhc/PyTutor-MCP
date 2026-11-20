import test from 'node:test';
import assert from 'node:assert/strict';
import { formatShare, formatCount, SHARE_PERCENT_MIN_N } from './share.js';

test('mẫu nhỏ chỉ hiện k/n, không có phần trăm', () => {
  assert.equal(formatShare(2, 6), '2/6');
  assert.equal(formatShare(0, 9), '0/9');
});

test('n >= 10 thêm phần trăm làm tròn', () => {
  assert.equal(SHARE_PERCENT_MIN_N, 10);
  assert.equal(formatShare(3, 10), '3/10 (30%)');
  assert.equal(formatShare(7, 12), '7/12 (58%)');
});

test('mẫu rỗng và đầu vào lạ không lỗi', () => {
  assert.equal(formatShare(0, 0), '0/0');
  assert.equal(formatShare(undefined, undefined), '0/0');
  assert.equal(formatCount(3, 'lượt'), '3 lượt');
  assert.equal(formatCount(null), '0');
});
