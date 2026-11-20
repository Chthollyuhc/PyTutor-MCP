import test from 'node:test';
import assert from 'node:assert/strict';
import { isBlankCode } from './blankCode.js';

test('rỗng, chỉ bình luận, pass hoặc ... là chưa có code', () => {
  assert.equal(isBlankCode(''), true);
  assert.equal(isBlankCode('  \n# viết code ở đây\npass\n'), true);
  assert.equal(isBlankCode('...'), true);
});
test('y hệt khung mẫu là chưa có code', () => {
  assert.equal(isBlankCode('n = int(input())\n# TODO', 'n = int(input())\n'), true);
});
test('có thêm dòng thật thì không còn trống', () => {
  assert.equal(isBlankCode('n = int(input())\nprint(n)', 'n = int(input())'), false);
  assert.equal(isBlankCode('print(1)'), false);
});
