import React, { useState, useEffect } from 'react';
import {
  X,
  Award,
  BarChart2,
  BookOpen,
  Clock,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Sparkles,
  Zap,
  TrendingUp,
  Target,
  AlertCircle
} from 'lucide-react';
import { fetchStudentProfile } from '../services/api';
import { useAuth } from '../context/AuthContext';

/**
 * StudentProfileModal - Hồ sơ Đánh giá Năng lực Học viên & Phân tích 4 Chiều (LMS-ITS NEU)
 * Bao gồm:
 * 1. Phân hạng Năng lực Chuẩn NEU (Level Classification)
 * 2. 3 Thẻ Chẩn đoán Dữ liệu Sư phạm:
 *    - Điểm mạnh Nổi bật
 *    - Điểm nghẽn Cần khắc phục
 *    - Hành động Khuyến nghị Tiếp theo
 * 3. Động cơ Phân tích 4 Chiều:
 *    - Điểm Tự lực Sư phạm (Autonomy Score / 100)
 *    - Tỷ lệ Pass Lần đầu (First-try Pass Rate %)
 *    - Số lần nộp trung bình / bài giải
 *    - Phân bổ Cơ cấu Lỗi (Error Breakdown: Pass, Logic, Syntax/Runtime)
 * 4. Lịch sử làm bài gần nhất & Nạp lại mã nguồn
 */
export default function StudentProfileModal({
  isOpen,
  onClose,
  sessionId,
  classId,
  currentExerciseId,
  onLoadCode,
  studentName = 'Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)'
}) {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || !sessionId) return;

    const loadProfile = async () => {
      setIsLoading(true);
      try {
        const data = await fetchStudentProfile(sessionId, currentExerciseId, classId);
        setProfile(data);
      } catch (err) {
        console.error('Lỗi khi tải hồ sơ năng lực học viên:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadProfile();
  }, [isOpen, sessionId, currentExerciseId, classId]);

  if (!isOpen) return null;

  const am = profile?.analytics_metrics || {};
  const diag = profile?.diagnostic_evaluation || {};
  const errBreakdown = am.error_breakdown || {
    total_runs: 0,
    passed_runs: 0,
    passed_percent: 0,
    logic_errors: 0,
    logic_error_percent: 0,
    syntax_or_runtime_errors: 0,
    syntax_error_percent: 0
  };

  const autonomyScore = am.autonomy_score !== undefined ? am.autonomy_score : 70;
  const firstTryPassRate = am.first_try_pass_rate !== undefined ? am.first_try_pass_rate : 0;
  const avgAttempts = am.avg_attempts_to_solve !== undefined ? am.avg_attempts_to_solve : 1.0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-md select-text animate-fade-in">
      <div className="w-full max-w-3xl max-h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-lg shadow-sky-950/40">
              📊
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                  Hồ Sơ Năng Lực & Chẩn Đoán Sư Phạm NEU
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-sky-950 text-sky-400 border border-sky-800">
                  Chuẩn Tín Chỉ
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                {user?.full_name || 'Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)'} • Khoa Công nghệ thông tin - NEU
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Level Classification Banner */}
        <div className="px-6 py-3 bg-gradient-to-r from-sky-950/60 via-indigo-950/40 to-slate-950 border-b border-slate-800 flex items-center justify-between flex-wrap gap-2 shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-300 font-medium">Phân hạng Năng lực:</span>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-sky-900/60 text-sky-300 border border-sky-700/80 flex items-center gap-1.5 shadow-sm">
              <span>🎓</span>
              <span>{diag.level_classification || 'Đang thẩm định năng lực'}</span>
            </span>
          </div>
          <div className="text-xs text-slate-400 flex items-center gap-3">
            <span>Đã làm chủ: <strong className="text-emerald-400">{profile?.mastered_exercises?.length || 0}</strong> bài</span>
            <span>•</span>
            <span>Tổng lượt chạy: <strong className="text-sky-300">{profile?.total_submissions || 0}</strong></span>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs">
          {isLoading ? (
            <div className="py-16 text-center text-slate-500 space-y-2">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-400 mx-auto" />
              <p>Đang tổng hợp dữ liệu phân tích năng lực 4 chiều...</p>
            </div>
          ) : profile ? (
            <>
              {/* PHẦN 1: 4D QUANTITATIVE LEARNING ANALYTICS */}
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                  <BarChart2 className="w-4 h-4 text-sky-400" />
                  <span>Động cơ Phân tích Năng lực 4 Chiều (Quantitative 4D Metrics)</span>
                </h3>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {/* Metric 1: Autonomy Score */}
                  <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                      <span className="text-slate-400 text-[10.5px] block mb-1">Điểm Tự Lực (Autonomy)</span>
                      <div className="text-2xl font-bold font-mono text-emerald-400">
                        {autonomyScore}<span className="text-xs text-slate-500 font-normal">/100</span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5 mt-2 overflow-hidden">
                      <div
                        className="bg-emerald-500 h-1.5 rounded-full"
                        style={{ width: `${Math.min(100, Math.max(0, autonomyScore))}%` }}
                      />
                    </div>
                  </div>

                  {/* Metric 2: First-try Pass Rate */}
                  <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                      <span className="text-slate-400 text-[10.5px] block mb-1">Pass Ngay Lần Đầu</span>
                      <div className="text-2xl font-bold font-mono text-sky-400">
                        {firstTryPassRate}<span className="text-xs text-slate-500 font-normal">%</span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5 mt-2 overflow-hidden">
                      <div
                        className="bg-sky-500 h-1.5 rounded-full"
                        style={{ width: `${Math.min(100, Math.max(0, firstTryPassRate))}%` }}
                      />
                    </div>
                  </div>

                  {/* Metric 3: Avg Attempts */}
                  <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                      <span className="text-slate-400 text-[10.5px] block mb-1">Số Lần Nộp TB / Bài</span>
                      <div className="text-2xl font-bold font-mono text-amber-400">
                        {avgAttempts}<span className="text-xs text-slate-500 font-normal"> lượt</span>
                      </div>
                    </div>
                    <span className="text-[10px] text-slate-500 mt-2 block">
                      {avgAttempts <= 2 ? '⚡ Giải quyết rất nhanh' : '🔄 Thử và sửa nhiều lần'}
                    </span>
                  </div>

                  {/* Metric 4: Hint Level */}
                  <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                      <span className="text-slate-400 text-[10.5px] block mb-1">Mức Gợi Ý TB</span>
                      <div className="text-2xl font-bold font-mono text-indigo-400">
                        L{profile.average_hint_level || 1.0}
                      </div>
                    </div>
                    <span className="text-[10px] text-slate-500 mt-2 block">
                      {profile.average_hint_level <= 1.5 ? '⭐ Độc lập tư duy cao' : '💡 Sử dụng trợ giúp AI'}
                    </span>
                  </div>
                </div>

                {/* Error Breakdown Stacked Bar */}
                <div className="mt-3 p-3.5 bg-slate-950/60 rounded-xl border border-slate-800/80">
                  <div className="flex justify-between items-center text-xs mb-2">
                    <span className="font-semibold text-slate-300">Phân bổ Cơ cấu Kết quả Thực thi & Lỗi:</span>
                    <span className="text-slate-400 font-mono text-[11px]">{errBreakdown.total_runs} lượt chạy Sandbox</span>
                  </div>

                  {/* Stacked Bar */}
                  <div className="w-full bg-slate-900 rounded-lg h-3 flex overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full transition-all"
                      style={{ width: `${errBreakdown.passed_percent}%` }}
                      title={`Đạt 100%: ${errBreakdown.passed_runs} (${errBreakdown.passed_percent}%)`}
                    />
                    <div
                      className="bg-amber-500 h-full transition-all"
                      style={{ width: `${errBreakdown.logic_error_percent}%` }}
                      title={`Lỗi Logic: ${errBreakdown.logic_errors} (${errBreakdown.logic_error_percent}%)`}
                    />
                    <div
                      className="bg-rose-500 h-full transition-all"
                      style={{ width: `${errBreakdown.syntax_error_percent}%` }}
                      title={`Lỗi Cú pháp / Runtime: ${errBreakdown.syntax_or_runtime_errors} (${errBreakdown.syntax_error_percent}%)`}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 flex-wrap gap-2">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block" />
                      <span>Pass 100%: <strong>{errBreakdown.passed_runs}</strong> ({errBreakdown.passed_percent}%)</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-sm bg-amber-500 inline-block" />
                      <span>Lỗi Logic / Test Fail: <strong>{errBreakdown.logic_errors}</strong> ({errBreakdown.logic_error_percent}%)</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-sm bg-rose-500 inline-block" />
                      <span>Lỗi Cú pháp / Ngoại lệ: <strong>{errBreakdown.syntax_or_runtime_errors}</strong> ({errBreakdown.syntax_error_percent}%)</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* PHẦN 2: 3 THẺ CHẨN ĐOÁN DỮ LIỆU SƯ PHẠM (DIAGNOSTIC CARDS) */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  <span>3 Thẻ Chẩn đoán Sư phạm Thích ứng (AI Diagnostic Feedback)</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {/* Card 1: Điểm mạnh */}
                  <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/60 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center gap-1.5 text-emerald-400 font-bold mb-2">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>1. Điểm mạnh Nổi bật</span>
                      </div>
                      <p className="text-slate-200 text-xs leading-relaxed">
                        {diag.strengths_analysis || 'Chưa có đủ dữ liệu để đánh giá điểm mạnh.'}
                      </p>
                    </div>
                  </div>

                  {/* Card 2: Điểm nghẽn */}
                  <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/60 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center gap-1.5 text-amber-300 font-bold mb-2">
                        <AlertCircle className="w-4 h-4" />
                        <span>2. Điểm nghẽn Cần khắc phục</span>
                      </div>
                      <p className="text-slate-200 text-xs leading-relaxed">
                        {diag.weaknesses_and_bottlenecks || 'Chưa ghi nhận điểm nghẽn nghiêm trọng nào.'}
                      </p>
                    </div>
                  </div>

                  {/* Card 3: Hành động Khuyến nghị */}
                  <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-800/60 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center gap-1.5 text-sky-400 font-bold mb-2">
                        <Target className="w-4 h-4" />
                        <span>3. Hành động Khuyến nghị</span>
                      </div>
                      <p className="text-slate-200 text-xs leading-relaxed">
                        {diag.recommended_next_action || 'Tiếp tục luyện tập theo Lộ trình kỹ năng của Lớp học phần.'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* PHẦN 3: LỊCH SỬ NỘP BÀI GẦN ĐÂY */}
              <div className="space-y-2.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                  <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Lịch sử các lần nộp bài gần đây (kèm mã nguồn):</span>
                </span>

                {profile.recent_attempts && profile.recent_attempts.length > 0 ? (
                  <div className="space-y-2">
                    {profile.recent_attempts.map((att, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-between flex-wrap gap-2 hover:border-slate-700 transition-colors"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                att.all_passed
                                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                              }`}
                            >
                              {att.all_passed ? 'ĐẠT 100%' : 'CHƯA ĐẠT'}
                            </span>
                            <span className="text-slate-300 font-medium">
                              Đạt {att.passed}/{att.total} test cases
                            </span>
                            <span className="text-slate-500 text-[11px]">•</span>
                            <span className="text-amber-400 font-mono text-[11px]">Gợi ý Mức {att.hint_level}</span>
                          </div>
                          <p className="text-[10.5px] text-slate-500">{att.timestamp}</p>
                        </div>

                        {att.code && (
                          <button
                            type="button"
                            onClick={() => {
                              if (onLoadCode) onLoadCode(att.code);
                              onClose();
                            }}
                            className="flex items-center space-x-1.5 py-1 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 rounded-lg transition-colors cursor-pointer text-xs font-medium"
                            title="Nạp lại mã nguồn lần nộp này vào khung soạn thảo"
                          >
                            <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
                            <span>⏪ Nạp lại code lần này</span>
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 italic p-3 bg-slate-950 rounded-xl border border-slate-800 text-center">
                    Chưa có lịch sử nộp bài nào cho bài tập này.
                  </p>
                )}
              </div>
            </>
          ) : (
            <p className="text-slate-500 text-center py-6">Không có dữ liệu nhật ký học tập.</p>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex items-center justify-between shrink-0 text-xs text-slate-400">
          <span>Khoa Công nghệ thông tin - Đại học Kinh tế Quốc dân (NEU)</span>
          <button
            type="button"
            onClick={onClose}
            className="py-1.5 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition-colors cursor-pointer"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}
