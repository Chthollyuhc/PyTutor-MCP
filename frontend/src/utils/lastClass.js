// Ghi nhớ lớp học phần sinh viên mở gần nhất để trang chủ vẽ "chặng đường" đúng học phần (các lớp dùng chung bài tập).
const KEY = 'pytutor_last_class_id';

export function rememberLastClassId(classId, storage = globalThis.localStorage) {
  if (!classId) return;
  try {
    storage?.setItem(KEY, String(classId));
  } catch {
    /* localStorage có thể bị chặn: bỏ qua, trang chủ dùng cách chọn mặc định */
  }
}

export function readLastClassId(storage = globalThis.localStorage) {
  try {
    return storage?.getItem(KEY) || null;
  } catch {
    return null;
  }
}
