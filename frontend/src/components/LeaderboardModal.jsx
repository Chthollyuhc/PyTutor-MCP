import React, { useState, useEffect } from 'react';
import {
  X,
  Trophy,
  Award,
  Star,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  User,
  ShieldCheck,
  Medal
} from 'lucide-react';
import { fetchLeaderboard } from '../services/api';

export default function LeaderboardModal({
  isOpen,
  onClose,
}) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    const loadData = async () => {
      setIsLoading(true);
      try {
        const data = await fetchLeaderboard(25);
        setLeaderboard(data.leaderboard || []);
      } catch (err) {
        console.error('Lỗi khi tải bảng xếp hạng:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [isOpen]);

  if (!isOpen) return null;

  const top1 = leaderboard[0] || null;
  const top2 = leaderboard[1] || null;
  const top3 = leaderboard[2] || null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/85 backdrop-blur-md select-text animate-fade-in">
      <div className="w-full max-w-4xl max-h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 font-bold">
              <Trophy className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                  🏆 Bảng Vàng Lớp Học & Vinh Danh Sao Tự Lực
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 font-medium">
                  Leaderboard
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Xếp hạng dựa trên Tổng số Sao Tự lực (⭐), Số bài giải đúng và Điểm Clean Code
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            type="button"
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
            title="Đóng cửa sổ"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {isLoading ? (
            <div className="h-64 flex items-center justify-center text-slate-400 space-x-2">
              <RefreshCw className="w-5 h-5 animate-spin text-amber-400" />
              <span>Đang tải bảng vàng lớp học...</span>
            </div>
          ) : (
            <>
              {/* Podium Top 3 Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end pt-2">
                {/* Rank 2 (Silver) */}
                {top2 ? (
                  <div className="order-2 sm:order-1 p-3.5 rounded-xl bg-slate-900 border border-slate-700/80 flex flex-col items-center text-center shadow-md">
                    <span className="text-2xl mb-1">🥈</span>
                    <span className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">
                      Hạng Nhì
                    </span>
                    <h3 className="text-sm font-bold text-white mt-1 line-clamp-1">
                      {top2.full_name}
                    </h3>
                    <div className="flex items-center space-x-1 text-amber-400 font-bold text-xs mt-1">
                      <Star className="w-3.5 h-3.5 fill-current" />
                      <span>{top2.total_stars} Sao</span>
                    </div>
                    <span className="text-[11px] text-slate-400 mt-0.5">
                      {top2.completed_exercises} bài giải đúng
                    </span>
                    <div className="flex items-center space-x-1 mt-2 text-xs">
                      {top2.badges?.map((b, idx) => (
                        <span key={idx} title={b.title} className="text-sm">{b.icon}</span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="order-2 sm:order-1 p-3.5 rounded-xl border border-dashed border-slate-800 text-center text-slate-600 text-xs">
                    Đang chờ cập nhật
                  </div>
                )}

                {/* Rank 1 (Gold) */}
                {top1 ? (
                  <div className="order-1 sm:order-2 p-4 rounded-xl bg-gradient-to-b from-amber-500/15 via-slate-900 to-slate-900 border-2 border-amber-500/50 flex flex-col items-center text-center shadow-xl shadow-amber-950/30 -translate-y-1">
                    <span className="text-3xl mb-1">👑</span>
                    <span className="text-[11px] font-extrabold uppercase text-amber-400 tracking-wider">
                      Quán Quân 🥇
                    </span>
                    <h3 className="text-base font-extrabold text-white mt-1 line-clamp-1">
                      {top1.full_name}
                    </h3>
                    <div className="flex items-center space-x-1.5 text-amber-300 font-extrabold text-sm mt-1 bg-amber-500/20 px-3 py-0.5 rounded-full border border-amber-500/40">
                      <Star className="w-4 h-4 fill-current text-amber-400" />
                      <span>{top1.total_stars} Sao Tự Lực</span>
                    </div>
                    <span className="text-xs text-slate-300 mt-1">
                      {top1.completed_exercises} bài • Clean Max: {top1.highest_clean_score}
                    </span>
                    <div className="flex items-center space-x-1.5 mt-2.5 text-sm">
                      {top1.badges?.map((b, idx) => (
                        <span key={idx} title={b.title} className="text-base hover:scale-125 transition-transform">{b.icon}</span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="order-1 sm:order-2 p-4 rounded-xl border border-dashed border-slate-800 text-center text-slate-600 text-xs">
                    Chưa có học viên
                  </div>
                )}

                {/* Rank 3 (Bronze) */}
                {top3 ? (
                  <div className="order-3 p-3.5 rounded-xl bg-slate-900 border border-slate-700/80 flex flex-col items-center text-center shadow-md">
                    <span className="text-2xl mb-1">🥉</span>
                    <span className="text-[11px] font-bold uppercase text-amber-600 tracking-wider">
                      Hạng Ba
                    </span>
                    <h3 className="text-sm font-bold text-white mt-1 line-clamp-1">
                      {top3.full_name}
                    </h3>
                    <div className="flex items-center space-x-1 text-amber-400 font-bold text-xs mt-1">
                      <Star className="w-3.5 h-3.5 fill-current" />
                      <span>{top3.total_stars} Sao</span>
                    </div>
                    <span className="text-[11px] text-slate-400 mt-0.5">
                      {top3.completed_exercises} bài giải đúng
                    </span>
                    <div className="flex items-center space-x-1 mt-2 text-xs">
                      {top3.badges?.map((b, idx) => (
                        <span key={idx} title={b.title} className="text-sm">{b.icon}</span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="order-3 p-3.5 rounded-xl border border-dashed border-slate-800 text-center text-slate-600 text-xs">
                    Đang chờ cập nhật
                  </div>
                )}
              </div>

              {/* Full Leaderboard Table */}
              <div className="border border-slate-800 rounded-xl bg-slate-950 overflow-hidden">
                <div className="px-4 py-2.5 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between text-xs text-slate-300 font-semibold">
                  <span>DANH SÁCH CHI TIẾT HỌC VIÊN</span>
                  <span className="text-slate-500 font-normal">Sắp xếp theo Tổng Sao & Bài giải</span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-[11px] text-slate-400 uppercase font-semibold">
                        <th className="py-2.5 pl-4">Hạng</th>
                        <th className="py-2.5">Học viên</th>
                        <th className="py-2.5 text-center">Tổng Sao (⭐)</th>
                        <th className="py-2.5 text-center">Bài đã giải</th>
                        <th className="py-2.5 text-center">Điểm Clean Max</th>
                        <th className="py-2.5 pr-4 text-right">Huy hiệu đạt được</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-sans">
                      {leaderboard.map((item) => (
                        <tr key={item.username} className="hover:bg-slate-900/50 transition-colors">
                          <td className="py-2.5 pl-4 font-bold text-slate-400">
                            {item.rank === 1 ? '🥇' : item.rank === 2 ? '🥈' : item.rank === 3 ? '🥉' : `#${item.rank}`}
                          </td>
                          <td className="py-2.5">
                            <div className="font-semibold text-white">{item.full_name}</div>
                            <div className="text-[10.5px] font-mono text-slate-500">{item.username}</div>
                          </td>
                          <td className="py-2.5 text-center">
                            <span className="font-extrabold text-amber-400 font-mono text-sm">
                              {item.total_stars} ⭐
                            </span>
                          </td>
                          <td className="py-2.5 text-center text-slate-300 font-medium">
                            {item.completed_exercises}
                          </td>
                          <td className="py-2.5 text-center">
                            <span className="px-2 py-0.5 rounded bg-slate-800 text-emerald-400 font-mono font-bold text-[11px]">
                              {item.highest_clean_score || 0}
                            </span>
                          </td>
                          <td className="py-2.5 pr-4 text-right">
                            {item.badges && item.badges.length > 0 ? (
                              <div className="flex items-center justify-end space-x-1">
                                {item.badges.map((b, idx) => (
                                  <span key={idx} title={b.title} className="text-sm cursor-help">
                                    {b.icon}
                                  </span>
                                ))}
                              </div>
                            ) : (
                              <span className="text-slate-600 text-[11px] italic">Chưa có</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Badges Legend / Showcase */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                <span className="font-bold text-slate-200 block mb-2">
                  🎖️ BỘ SƯU TẬP 5 HUY HIỆU DANH GIÁ
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-[11.5px] text-slate-400">
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center space-x-2">
                    <span className="text-lg">🌟</span>
                    <div>
                      <div className="font-semibold text-slate-200">Bước Chân Đầu Tiên</div>
                      <div className="text-[10px] text-slate-500">Hoàn thành bài tập đầu tiên</div>
                    </div>
                  </div>

                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center space-x-2">
                    <span className="text-lg">🏆</span>
                    <div>
                      <div className="font-semibold text-slate-200">Bậc Thầy Tự Lực</div>
                      <div className="text-[10px] text-slate-500">Đạt 3 Sao ở 3 bài khác nhau</div>
                    </div>
                  </div>

                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center space-x-2">
                    <span className="text-lg">⚡</span>
                    <div>
                      <div className="font-semibold text-slate-200">Thợ Săn Lỗi Tự Thân</div>
                      <div className="text-[10px] text-slate-500">Sửa thành công sau khi từng fail</div>
                    </div>
                  </div>

                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center space-x-2">
                    <span className="text-lg">🐍</span>
                    <div>
                      <div className="font-semibold text-slate-200">Nhà Khai Phá Pythonic</div>
                      <div className="text-[10px] text-slate-500">Clean Code &gt;= 90 điểm</div>
                    </div>
                  </div>

                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center space-x-2">
                    <span className="text-lg">🧗</span>
                    <div>
                      <div className="font-semibold text-slate-200">Kiên Trì Bền Bỉ</div>
                      <div className="text-[10px] text-slate-500">Hoàn thành bài sau &gt; 5 lần thử</div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
