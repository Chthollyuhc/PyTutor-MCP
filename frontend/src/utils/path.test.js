import test from 'node:test';
import assert from 'node:assert/strict';
import { windowSteps } from './path.js';

const mk = (kinds) => kinds.map((kind, i) => ({ exercise_id: `e${i + 1}`, kind }));

test('ít trạm thì hiện hết', () => {
  const r = windowSteps(mk(['done', 'current', 'open']), 8);
  assert.equal(r.visible.length, 3);
  assert.equal(r.hiddenBefore, 0);
  assert.equal(r.hiddenAfter, 0);
});

test('nhiều trạm thì giữ bài đang làm trong cửa sổ', () => {
  const kinds = Array.from({ length: 12 }, (_, i) => (i < 6 ? 'done' : i === 6 ? 'current' : 'locked'));
  const r = windowSteps(mk(kinds), 8);
  assert.equal(r.visible.length, 8);
  assert.equal(r.hiddenBefore, 3);
  assert.equal(r.hiddenAfter, 1);
  assert.ok(r.visible.some((s) => s.kind === 'current'));
});

test('bài đang làm ở cuối danh sách', () => {
  const kinds = Array.from({ length: 12 }, (_, i) => (i < 11 ? 'done' : 'current'));
  const r = windowSteps(mk(kinds), 8);
  assert.equal(r.hiddenBefore, 4);
  assert.equal(r.hiddenAfter, 0);
});

test('không có bài đang làm thì lấy bài đầu tiên chưa xong', () => {
  const kinds = Array.from({ length: 12 }, (_, i) => (i < 10 ? 'done' : 'locked'));
  const r = windowSteps(mk(kinds), 8);
  assert.ok(r.visible.some((s) => s.exercise_id === 'e11'));
});

test('xong hết thì hiện các trạm cuối', () => {
  const r = windowSteps(mk(Array(12).fill('done')), 8);
  assert.equal(r.hiddenBefore, 4);
  assert.equal(r.hiddenAfter, 0);
});
