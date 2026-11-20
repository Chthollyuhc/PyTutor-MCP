/** Hiển thị tỉ lệ trên mẫu nhỏ (v5.8). Quy ước trình bày: luôn hiện k/n; chỉ thêm % khi n >= SHARE_PERCENT_MIN_N. */
export const SHARE_PERCENT_MIN_N = 10;

export function formatShare(k, n) {
  const kk = Number(k) || 0;
  const nn = Number(n) || 0;
  if (nn <= 0) return '0/0';
  const base = `${kk}/${nn}`;
  return nn >= SHARE_PERCENT_MIN_N ? `${base} (${Math.round((kk / nn) * 100)}%)` : base;
}

/** Đếm kèm đơn vị: formatCount(3, 'lượt') -> "3 lượt". */
export function formatCount(n, unit = '') {
  const nn = Number(n) || 0;
  return unit ? `${nn} ${unit}` : String(nn);
}
