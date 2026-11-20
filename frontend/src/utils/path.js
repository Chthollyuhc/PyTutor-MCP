/** Cửa sổ trạm cho chặng đường học phần: tối đa `max` trạm quanh bài đang làm. Hàm thuần. */
export function windowSteps(steps, max = 8) {
  const list = Array.isArray(steps) ? steps : [];
  if (list.length <= max) return { visible: list, hiddenBefore: 0, hiddenAfter: 0 };
  let c = list.findIndex((s) => s.kind === 'current');
  if (c < 0) c = list.findIndex((s) => s.kind !== 'done');
  if (c < 0) c = list.length - 1;
  let start = Math.max(0, c - 3);
  const end = Math.min(list.length, start + max);
  start = Math.max(0, end - max);
  return { visible: list.slice(start, end), hiddenBefore: start, hiddenAfter: list.length - end };
}
