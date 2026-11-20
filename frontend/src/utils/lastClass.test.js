import test from 'node:test';
import assert from 'node:assert/strict';
import { rememberLastClassId, readLastClassId } from './lastClass.js';

const memory = () => {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, v) };
};

test('ghi nhớ và đọc lại lớp vừa mở', () => {
  const s = memory();
  assert.equal(readLastClassId(s), null);
  rememberLastClassId('cls_a', s);
  assert.equal(readLastClassId(s), 'cls_a');
  rememberLastClassId('cls_b', s);
  assert.equal(readLastClassId(s), 'cls_b');
});

test('bỏ qua giá trị rỗng, không ghi đè lớp đã nhớ', () => {
  const s = memory();
  rememberLastClassId('cls_a', s);
  rememberLastClassId(null, s);
  rememberLastClassId('', s);
  assert.equal(readLastClassId(s), 'cls_a');
});

test('localStorage bị chặn (ném lỗi) thì không làm hỏng trang', () => {
  const blocked = { getItem: () => { throw new Error('blocked'); }, setItem: () => { throw new Error('blocked'); } };
  assert.doesNotThrow(() => rememberLastClassId('x', blocked));
  assert.equal(readLastClassId(blocked), null);
  assert.equal(readLastClassId(undefined), null);
});
