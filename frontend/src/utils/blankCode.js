// Khớp với backend/adaptive_policy.is_blank_attempt: chưa có dòng code thật (rỗng, chỉ bình luận/pass/..., hoặc y hệt khung mẫu).
const meaningful = (src) => (src || '')
  .split('\n')
  .map((ln) => ln.trim())
  .filter((ln) => ln && !ln.startsWith('#') && ln !== 'pass' && ln !== '...');

export function isBlankCode(code, starterCode = '') {
  const mine = meaningful(code);
  if (mine.length === 0) return true;
  const starter = meaningful(starterCode);
  return mine.length === starter.length && mine.every((ln, i) => ln === starter[i]);
}
