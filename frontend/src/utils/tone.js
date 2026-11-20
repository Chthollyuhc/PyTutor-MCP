/**
 * Tiện ích ánh xạ tông màu lớp học phần và mức độ bài tập sang variant Badge.
 */

const TONE_COUNT = 5;

export function toneIndex(classes = [], classId = '') {
  if (!Array.isArray(classes) || !classes.length || !classId) {
    return 0;
  }
  const idx = classes.findIndex((item) => item?.id === classId);
  if (idx >= 0) {
    return idx % TONE_COUNT;
  }
  let hash = 0;
  for (let i = 0; i < classId.length; i += 1) {
    hash = (hash * 31 + classId.charCodeAt(i)) >>> 0;
  }
  return hash % TONE_COUNT;
}

export function difficultyVariant(difficulty) {
  switch (difficulty) {
    case 'Dễ':
      return 'success';
    case 'Trung bình':
      return 'warning';
    case 'Khó':
      return 'danger';
    default:
      return 'neutral';
  }
}
