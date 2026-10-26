import React, { useState, useEffect } from 'react';
import {
  X,
  Sparkles,
  CheckCircle2,
  Award,
  Zap,
  Code2,
  Copy,
  Check,
  RefreshCw,
  Lightbulb,
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { requestPythonicReview } from '../services/api';

export default function PythonicReviewModal({
  isOpen,
  onClose,
  exerciseId,
  code,
  username = 'student',
  starsEarned = 3,
}) {
  const [review, setReview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('pythonic'); // 'pythonic' | 'student'

  useEffect(() => {
    if (!isOpen || !exerciseId || !code) return;

    const loadReview = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await requestPythonicReview({
          exercise_id: exerciseId,
          code,
          username,
        });
        setReview(data);
      } catch (err) {
        console.error('Lỗi khi review Pythonic:', err);
        setError('Không thể kết nối với Senior Python AI. Vui lòng thử lại sau.');
      } finally {
        setIsLoading(false);
      }
    };

    loadReview();
  }, [isOpen, exerciseId, code, username]);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!review?.pythonic_code) return;
    navigator.clipboard.writeText(review.pythonic_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const cleanScore = review?.clean_score || 85;

  const getScoreBadge = (score) => {
    if (score >= 90) return { label: 'Bậc Thầy Pythonic (Master)', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' };
    if (score >= 80) return { label: 'Rất Tốt & Rõ Ràng (Clean Code)', color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30' };
    return { label: 'Đạt Chuẩn Cơ Bản (Functional)', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' };
  };

  const badgeInfo = getScoreBadge(cleanScore);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/85 backdrop-blur-md select-text animate-fade-in">
      <div className="w-full max-w-3xl max-h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500/20 to-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                  🚀 Thử thách Tối ưu Code Chuẩn Pythonic
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-medium">
                  Senior Review
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Nâng tầm phong cách lập trình từ code chạy được thành code thanh lịch, tối ưu (PEP 8)
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
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {isLoading ? (
            <div className="h-72 flex flex-col items-center justify-center space-y-3 text-slate-400">
              <RefreshCw className="w-8 h-8 animate-spin text-emerald-400" />
              <p className="text-sm font-medium text-slate-300">
                Senior Python Architect đang phân tích mã nguồn của bạn...
              </p>
              <p className="text-xs text-slate-500">
                Đánh giá cấu trúc AST, đối chiếu tiêu chuẩn PEP 8 và các thành ngữ Pythonic
              </p>
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-sm text-center">
              {error}
            </div>
          ) : review ? (
            <>
              {/* Score & Stars Banner */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center space-x-4">
                  {/* Circular Score Gauge */}
                  <div className="w-16 h-16 rounded-full bg-slate-900 border-2 border-emerald-500 flex flex-col items-center justify-center shrink-0 shadow-lg shadow-emerald-950/50">
                    <span className="text-xl font-extrabold text-emerald-400 leading-none">
                      {cleanScore}
                    </span>
                    <span className="text-[9px] text-slate-400 font-mono">/ 100</span>
                  </div>

                  <div>
                    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeInfo.color} mb-1`}>
                      {badgeInfo.label}
                    </span>
                    <p className="text-xs text-slate-300 font-medium">
                      Điểm phong cách Clean Code & Tính thanh lịch
                    </p>
                  </div>
                </div>

                {/* Stars earned badge */}
                <div className="flex items-center space-x-2 bg-slate-900/90 border border-slate-800 px-3 py-2 rounded-xl">
                  <span className="text-xs text-slate-400 font-medium">Đánh giá tự lực:</span>
                  <div className="flex items-center space-x-1 text-base">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <span key={i} className={i < starsEarned ? 'text-amber-400' : 'text-slate-600'}>
                        ★
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Strengths & Improvements 2-Column Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {/* Strengths */}
                <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex flex-col">
                  <div className="flex items-center space-x-2 text-xs font-bold text-emerald-400 mb-2">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>ĐIỂM SÁNG TRONG CODE CỦA BẠN</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {review.strengths}
                  </p>
                </div>

                {/* Improvements */}
                <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/30 flex flex-col">
                  <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 mb-2">
                    <Lightbulb className="w-4 h-4 shrink-0" />
                    <span>CƠ HỘI NÂNG TẦM PYTHONIC</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {review.improvements}
                  </p>
                </div>
              </div>

              {/* Code Comparison Section */}
              <div className="border border-slate-800 rounded-xl bg-slate-950 overflow-hidden">
                <div className="px-4 py-2.5 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setActiveTab('pythonic')}
                      type="button"
                      className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                        activeTab === 'pythonic'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      🐍 Code Chuẩn Pythonic (Đề xuất)
                    </button>
                    <button
                      onClick={() => setActiveTab('student')}
                      type="button"
                      className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                        activeTab === 'student'
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      📝 Code Của Bạn
                    </button>
                  </div>

                  {activeTab === 'pythonic' && (
                    <button
                      onClick={handleCopy}
                      type="button"
                      className="flex items-center space-x-1 px-2.5 py-1 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md transition-colors cursor-pointer"
                    >
                      {copied ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-[11px] text-emerald-400">Đã sao chép!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span className="text-[11px]">Sao chép code</span>
                        </>
                      )}
                    </button>
                  )}
                </div>

                <div className="p-3.5 overflow-x-auto font-mono text-xs leading-6 text-slate-200">
                  <pre className="select-text whitespace-pre-wrap">
                    {activeTab === 'pythonic' ? review.pythonic_code : code}
                  </pre>
                </div>
              </div>

              {/* Explanation Card */}
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                <span className="font-bold text-cyan-400 flex items-center space-x-1.5 mb-1.5">
                  <TrendingUp className="w-4 h-4" />
                  <span>TẠI SAO ĐOẠN CODE NÀY LẠI TỐI ƯU HƠN?</span>
                </span>
                <p className="text-slate-300 leading-relaxed">
                  {review.explanation}
                </p>
              </div>

              {/* New Badges Notice if any */}
              {review.new_badges && review.new_badges.length > 0 && (
                <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center space-x-3 text-xs text-amber-300 animate-bounce">
                  <Award className="w-5 h-5 text-amber-400 shrink-0" />
                  <div>
                    <span className="font-bold">🎉 Chúc mừng bạn đã mở khóa huy hiệu mới: </span>
                    <span>
                      {review.new_badges.map(b => `${b.icon} ${b.title}`).join(', ')}!
                    </span>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
