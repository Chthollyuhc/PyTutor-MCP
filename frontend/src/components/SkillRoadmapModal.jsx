import React, { useState, useEffect } from 'react';
import {
  X,
  Map,
  CheckCircle2,
  Clock,
  Lock,
  Unlock,
  ArrowRight,
  Sparkles,
  RefreshCw,
  Award,
  AlertTriangle,
  Star
} from 'lucide-react';
import { fetchSkillRoadmap } from '../services/api';

/**
 * SkillRoadmapModal - Lộ trình Kỹ năng & Ma trận Chuẩn đầu ra Học phần NEU (Curriculum & Skill Matrix)
 * Hỗ trợ:
 * - Xem lộ trình kỹ năng theo từng Lớp học phần tín chỉ NEU (classId)
 * - Hiển thị Thang đo Định lượng (Mastery Rubric: min_stars_required, stars_earned)
 * - Phân nhóm bài tập theo từng Module / Chương học phần do Giảng viên thiết kế
 * - Cảnh báo trạng thái NEEDS_MORE_STARS khi học viên pass code nhưng lạm dụng gợi ý AI
 */
export default function SkillRoadmapModal({
  isOpen,
  onClose,
  sessionId,
  classId,
  onSelectExercise,
}) {
  const [roadmap, setRoadmap] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    const loadRoadmap = async () => {
      setIsLoading(true);
      try {
        const data = await fetchSkillRoadmap(sessionId, classId);
        setRoadmap(data);
      } catch (err) {
        console.error('Lỗi khi tải cây lộ trình:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadRoadmap();
  }, [isOpen, sessionId, classId]);

  if (!isOpen) return null;

  const nodes = roadmap?.nodes || [];
  const totalMastered = roadmap?.total_mastered || 0;
  const totalExercises = roadmap?.total_exercises || nodes.length || 1;
  const percentage = totalExercises > 0 ? Math.round((totalMastered / totalExercises) * 100) : 0;

  // Gom nhóm các bài tập theo module_name (nếu có) hoặc fallback theo danh sách
  const modulesMap = {};
  nodes.forEach((node) => {
    const mod = node.module_name || 'Học phần Lập trình Python';
    if (!modulesMap[mod]) {
      modulesMap[mod] = [];
    }
    modulesMap[mod].push(node);
  });

  const moduleSections = Object.keys(modulesMap).map((modName, idx) => ({
    order: idx + 1,
    title: modName,
    nodes: modulesMap[modName].sort((a, b) => (a.order_idx || 0) - (b.order_idx || 0)),
  }));

  const getStatusInfo = (status, minStars = 1, starsEarned = 0) => {
    switch (status) {
      case 'MASTERED':
        return {
          label: 'Đã làm chủ',
          badgeClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
          cardBorder: 'border-emerald-500/50 bg-emerald-950/20',
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
          actionText: 'Làm lại',
          isClickable: true,
        };
      case 'NEEDS_MORE_STARS':
        return {
          label: `Cần thêm sao (${starsEarned}/${minStars} ⭐)`,
          badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
          cardBorder: 'border-amber-500/50 bg-amber-950/20',
          icon: <AlertTriangle className="w-4 h-4 text-amber-400" />,
          actionText: 'Làm lại tự lực',
          isClickable: true,
        };
      case 'IN_PROGRESS':
        return {
          label: 'Đang thực hành',
          badgeClass: 'bg-sky-500/20 text-sky-400 border-sky-500/40',
          cardBorder: 'border-sky-500/40 bg-sky-950/20',
          icon: <Clock className="w-4 h-4 text-sky-400" />,
          actionText: 'Tiếp tục làm',
          isClickable: true,
        };
      case 'AVAILABLE':
        return {
          label: 'Sẵn sàng làm bài',
          badgeClass: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
          cardBorder: 'border-cyan-500/40 bg-slate-900',
          icon: <Unlock className="w-4 h-4 text-cyan-400" />,
          actionText: 'Bắt đầu giải',
          isClickable: true,
        };
      case 'LOCKED':
      default:
        return {
          label: 'Đang khóa',
          badgeClass: 'bg-slate-800 text-slate-500 border-slate-700',
          cardBorder: 'border-slate-800/80 bg-slate-900/40 opacity-75',
          icon: <Lock className="w-4 h-4 text-slate-500" />,
          actionText: 'Cần mở khóa',
          isClickable: false,
        };
    }
  };

  const handleCardClick = (node, statusInfo) => {
    if (!statusInfo.isClickable) return;
    if (onSelectExercise) onSelectExercise(node.id);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/85 backdrop-blur-md select-text animate-fade-in">
      <div className="w-full max-w-4xl max-h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-indigo-600 flex items-center justify-center text-amber-300 font-bold shadow-lg shadow-amber-950/40">
              <Map className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                  🗺️ Lộ trình Kỹ năng & Chuẩn Đầu Ra NEU
                </h2>
                {roadmap?.class_code && (
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800 font-bold">
                    {roadmap.class_code}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400">
                {roadmap?.class_name
                  ? `${roadmap.class_name} • Khoa Công nghệ thông tin - NEU`
                  : 'Sơ đồ phụ thuộc bài tập DAG kèm Thang đo Tự lực Định lượng (Mastery Rubric)'}
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

        {/* Mastery Rubric Explanation Banner */}
        <div className="px-6 py-2.5 bg-gradient-to-r from-amber-950/40 via-slate-950/60 to-sky-950/40 border-b border-slate-800 text-[11px] flex items-center justify-between flex-wrap gap-2 shrink-0">
          <div className="flex items-center gap-1.5 text-amber-300 font-medium">
            <span>⚖️ Thang đo Định lượng (Mastery Rubric):</span>
          </div>
          <div className="flex items-center gap-3 text-slate-300">
            <span className="flex items-center gap-1">
              <span className="text-amber-400">⭐⭐⭐</span>
              <span>Tự lực 100%</span>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <span className="text-amber-400">⭐⭐</span>
              <span>Gợi ý nhẹ (Level 1)</span>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <span className="text-amber-400">⭐</span>
              <span>Gợi ý sâu (Level 2-3)</span>
            </span>
          </div>
        </div>

        {/* Progress Bar & Legend Section */}
        <div className="px-6 py-3 bg-slate-950/80 border-b border-slate-800 shrink-0">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-200">
              <Award className="w-4 h-4 text-amber-400" />
              <span>Tiến độ Chuẩn đầu ra:</span>
              <span className="text-emerald-400 font-bold">{totalMastered} / {totalExercises} bài</span>
              <span className="text-slate-400">({percentage}%)</span>
            </div>

            {/* Legend */}
            <div className="flex items-center space-x-3 text-[11px] text-slate-400 select-none flex-wrap">
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
                <span>Đã làm chủ</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
                <span>Cần thêm sao</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-sky-400 inline-block" />
                <span>Đang thực hành</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block" />
                <span>Sẵn sàng</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-slate-600 inline-block" />
                <span>Đang khóa</span>
              </span>
            </div>
          </div>

          {/* Progress Bar Track */}
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 via-emerald-400 to-amber-400 transition-all duration-500 rounded-full"
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>

        {/* Roadmap Body - Tiered / Modular Nodes */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="h-64 flex items-center justify-center text-slate-400 space-x-2">
              <RefreshCw className="w-5 h-5 animate-spin text-amber-400" />
              <span>Đang tính toán cây kỹ năng thích ứng của Lớp học phần...</span>
            </div>
          ) : (
            moduleSections.map((sec, secIdx) => (
              <div key={sec.title} className="relative">
                {/* Connecting Line between Modules */}
                {secIdx < moduleSections.length - 1 && (
                  <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-slate-800 -z-0" />
                )}

                {/* Module Header */}
                <div className="flex items-start space-x-3 mb-3">
                  <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-sky-400 shrink-0 z-10 shadow-sm font-mono">
                    M{sec.order}
                  </div>
                  <div>
                    <h3 className="text-xs sm:text-sm font-bold text-slate-100 flex items-center gap-2">
                      <span>{sec.title}</span>
                    </h3>
                    <p className="text-[11px] text-slate-400">
                      Module đào tạo theo Đề cương chi tiết học phần Khoa CNTT - NEU
                    </p>
                  </div>
                </div>

                {/* Exercise Cards Grid */}
                <div className="ml-11 grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {sec.nodes.map((node) => {
                    const minStars = node.min_stars_required || 1;
                    const starsEarned = node.stars_earned || 0;
                    const statusInfo = getStatusInfo(node.status, minStars, starsEarned);

                    return (
                      <div
                        key={node.id}
                        onClick={() => handleCardClick(node, statusInfo)}
                        className={`p-4 rounded-xl border transition-all ${statusInfo.cardBorder} ${
                          statusInfo.isClickable
                            ? 'cursor-pointer hover:border-sky-500/60 hover:shadow-lg hover:scale-[1.01]'
                            : 'cursor-not-allowed'
                        }`}
                      >
                        {/* Title & Status */}
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h4 className="text-xs font-bold text-white line-clamp-1">
                            {node.title}
                          </h4>
                          <span
                            className={`flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border shrink-0 ${statusInfo.badgeClass}`}
                          >
                            {statusInfo.icon}
                            <span>{statusInfo.label}</span>
                          </span>
                        </div>

                        {/* Meta: Difficulty, Category, Skill Tag */}
                        <div className="flex items-center space-x-2 text-[11px] text-slate-400 mb-2 flex-wrap">
                          <span className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-medium">
                            {node.difficulty}
                          </span>
                          <span>•</span>
                          <span className="text-slate-300 font-medium">{node.category}</span>
                          {node.skill_tag && (
                            <>
                              <span>•</span>
                              <span className="text-sky-400 font-medium">{node.skill_tag}</span>
                            </>
                          )}
                        </div>

                        {/* Quantitative Mastery Rubric Row */}
                        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 mb-2 flex items-center justify-between text-[11px]">
                          <div className="flex items-center gap-1 text-slate-400">
                            <span>Yêu cầu chuẩn:</span>
                            <span className="text-amber-400 font-semibold flex items-center">
                              {Array.from({ length: minStars }).map((_, i) => (
                                <Star key={i} className="w-3 h-3 fill-amber-400 text-amber-400 inline" />
                              ))}
                              <span className="ml-1 text-[10px] text-slate-300">({minStars} ⭐)</span>
                            </span>
                          </div>
                          <div className="flex items-center gap-1 text-slate-400">
                            <span>Đã đạt:</span>
                            <span className={`font-bold flex items-center ${starsEarned >= minStars ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {starsEarned > 0 ? (
                                Array.from({ length: starsEarned }).map((_, i) => (
                                  <Star key={i} className="w-3 h-3 fill-current text-current inline" />
                                ))
                              ) : (
                                <span className="text-slate-500 font-normal">0 ⭐</span>
                              )}
                            </span>
                          </div>
                        </div>

                        {/* Prerequisites */}
                        {node.prerequisites && node.prerequisites.length > 0 && (
                          <div className="text-[10px] text-slate-500 mb-2 font-mono flex items-center space-x-1">
                            <span>Tiên quyết:</span>
                            <span className="text-slate-400">{node.prerequisites.join(', ')}</span>
                          </div>
                        )}

                        {/* Pedagogical Description / Prompt */}
                        {node.status_description && (
                          <p className="text-[10.5px] text-slate-400 mb-2.5 italic">
                            {node.status_description}
                          </p>
                        )}

                        {/* Action Call */}
                        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                          <span
                            className={`font-semibold flex items-center space-x-1 ${
                              statusInfo.isClickable ? 'text-sky-400' : 'text-slate-600'
                            }`}
                          >
                            <span>{statusInfo.actionText}</span>
                            {statusInfo.isClickable && <ArrowRight className="w-3.5 h-3.5" />}
                          </span>
                          <span className="text-[10px] font-mono text-slate-500">
                            {node.id}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
