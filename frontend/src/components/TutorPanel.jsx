import React, { useState, useEffect } from 'react';
import { Sparkles, HelpCircle, Compass, Code, ChevronRight, ChevronDown, ChevronUp, Send, MessageSquare, ShieldAlert, Star, Copy, Check, FileInput, Undo2 } from 'lucide-react';
import { Badge } from './ui';
import { sendTutorChatMessage } from '../services/api';
import TutorFeedbackButtons from './TutorFeedbackButtons';
import { groupTableLines, parseTable } from '../utils/hintMarkdown';

export default function TutorPanel({
  hintLevel,
  setHintLevel,
  astAnalysis,
  tutorHint,
  adaptiveStrategy,
  llmSource,
  isAskingAI = false,
  isSubmitting,
  testResults,
  onAskAI,
  onEscalate,
  onInsertSkeleton = null,
  canUndoInsert = false,
  onUndoInsert = null,
  exerciseId,
  code,
  sessionId,
  onOpenPythonicReview,
  starsEarned = 3,
  hintInteractionId = null,
  starRationale = null,
  isExamMode = false,
  currentSession = null,
  hasPassedBefore = false,
  classId = null,
}) {
  const [isAstOpen, setIsAstOpen] = useState(true);
  const [isStarRuleOpen, setIsStarRuleOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [userQuestion, setUserQuestion] = useState('');
  const [isSendingChat, setIsSendingChat] = useState(false);
  // v5.3 (S1.4): phạm vi chat do backend quyết định theo trạng thái nộp bài ('concept_only' | 'code_review').
  const [chatScope, setChatScope] = useState(null);

  // Khi học viên đổi bài tập, đặt lại lịch sử chat làm rõ
  useEffect(() => {
    setChatMessages([]);
    setUserQuestion('');
    setChatScope(null);
  }, [exerciseId]);

  // Vừa "Nộp bài" đạt (có star_rationale) hoặc backend xác nhận đã từng nộp đạt → mở hỏi về code đã nộp.
  // `hasPassedBefore` đến từ API chi tiết bài tập (đã nộp đạt ở phiên trước); backend vẫn là nơi quyết định phạm vi thật.
  const isCodeChatUnlocked = Boolean(starRationale) || hasPassedBefore || chatScope === 'code_review';

  // Mỗi mức một màu: 1 xanh ngọc (gợi mở), 2 cam (chẩn đoán), 3 tím (thuật toán chi tiết).
  const LEVEL_STYLE = {
    1: { bg: 'bg-success-soft', border: 'border-success-line', borderOn: 'border-success', ring: 'border-success', dot: 'bg-success', title: 'text-success-strong' },
    2: { bg: 'bg-warning-soft', border: 'border-warning-line', borderOn: 'border-warning', ring: 'border-warning', dot: 'bg-warning', title: 'text-warning-strong' },
    3: { bg: 'bg-ai-soft', border: 'border-ai-line', borderOn: 'border-ai', ring: 'border-ai', dot: 'bg-ai', title: 'text-ai-strong' },
  };

  const levels = [
    {
      level: 1,
      title: 'Mức 1 · Gợi mở tư duy',
      desc: 'Câu hỏi gợi mở giúp bạn tự nhớ lại khái niệm cốt lõi.',
      color: 'hover:border-emerald-500/60'
    },
    {
      level: 2,
      title: 'Mức 2 · Chẩn đoán lỗi',
      desc: 'Khoanh vùng dòng đáng xem, đối chiếu kiểm thử đạt với chưa đạt và nêu dãy giá trị khi chạy.',
      color: 'hover:border-amber-500/60'
    },
    {
      level: 3,
      title: 'Mức 3 · Thuật toán và khung code',
      desc: 'Thuật toán chi tiết bằng lời, các trường hợp cần xử lý và khung code có chỗ trống để bạn tự hoàn thiện.',
      color: 'hover:border-cyan-500/60'
    }
  ];

  const getLlmBadgeLabel = (source) => {
    if (!source) return 'Gia sư AI';
    const s = source.toLowerCase();
    if (s.includes('gemini')) return 'Gia sư AI · Gemini';
    if (s.includes('qwen')) return 'Gia sư AI · Qwen';
    return 'Gợi ý tự động';
  };

  // Gửi câu hỏi làm rõ tới Gia sư AI (Phase 8: Multi-turn Follow-up Chat)
  const handleSendChat = async (e) => {
    if (e) e.preventDefault();
    if (!userQuestion.trim() || isSendingChat) return;

    const currentMsg = userQuestion.trim();
    setUserQuestion('');
    const newHistory = [...chatMessages, { role: 'user', content: currentMsg }];
    setChatMessages(newHistory);
    setIsSendingChat(true);

    try {
      const res = await sendTutorChatMessage({
        exercise_id: exerciseId,
        code: code,
        session_id: sessionId,
        user_message: currentMsg,
        history: chatMessages,
        exam_session_id: currentSession?.id || null,
        class_id: classId || currentSession?.class_id || null,
      });

      if (res && res.reply) {
        if (res.chat_scope) setChatScope(res.chat_scope);
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: res.reply,
          interactionId: res.interaction_id,
          sources: Array.isArray(res.sources) ? res.sources : [],
          knowledgeStatus: res.knowledge_status || 'not_applicable',
        }]);
      }
    } catch (err) {
      console.error('Lỗi khi gửi câu hỏi tới Gia sư AI:', err);
      setChatMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Có lỗi kết nối khi trao đổi với Gia sư AI. Bạn vui lòng thử lại sau ít giây nhé.'
        }
      ]);
    } finally {
      setIsSendingChat(false);
    }
  };

  // Sao chỉ được ghi nhận ở lượt "Nộp bài" chính thức; chạy thử / hỏi AI không sinh star_rationale.
  const officialStars = starRationale ? Math.max(0, Math.min(3, Number(starRationale.stars) || 0)) : null;

  return (
    <div className="flex h-full select-text flex-col overflow-hidden bg-surface text-foreground">
      {/* Tiêu đề cột: màu tím = Gia sư AI */}
      <div className="on-brand flex min-h-12 shrink-0 items-center justify-between gap-2 bg-ai px-4 text-on-solid">
        <h2 className="flex items-center gap-2 text-sm font-bold">
          <Sparkles aria-hidden="true" className="size-4" />
          Gia sư PyTutor
        </h2>
        <span className="rounded-full bg-header-foreground/20 px-2.5 py-0.5 text-[0.8125rem] font-semibold">{getLlmBadgeLabel(llmSource)}</span>
      </div>

      <div className="flex-1 space-y-5 overflow-y-auto p-4 text-sm leading-relaxed">
        {/* Section 1: Hint Level Selector or Exam Mode Lock Notice */}
        {isExamMode ? (
          <div role="status" className="space-y-2 rounded-lg border border-warning-line bg-warning-soft p-4">
            <p className="flex items-center gap-2 font-bold text-warning-strong">
              <ShieldAlert aria-hidden="true" className="size-4 shrink-0" />
              Chế độ kỳ thi: Gia sư AI tạm khóa
            </p>
            <p className="text-[0.8125rem] text-foreground">
              Để đánh giá công bằng, hãy dùng “Chạy thử” và “Nộp bài” ở cột giữa. Hệ thống vẫn chấm điểm đầy đủ.
            </p>
          </div>
        ) : (
          <fieldset>
            <legend className="mb-2 flex items-center gap-1.5 text-sm font-bold">
              <Compass aria-hidden="true" className="size-4 text-ai-strong" />
              Bạn muốn gợi ý đến mức nào?
            </legend>

            <div role="radiogroup" aria-label="Mức gợi ý" className="grid grid-cols-1 gap-2">
              {levels.map((item) => {
                const active = hintLevel === item.level;
                const st = LEVEL_STYLE[item.level];
                return (
                  <button
                    key={item.level}
                    type="button"
                    role="radio"
                    aria-checked={active}
                    onClick={() => setHintLevel(item.level)}
                    className={`rounded-2xl border-2 px-3.5 py-3 text-left transition-all shadow-soft cursor-pointer ${st.bg} ${active ? st.borderOn : st.border}`}
                  >
                    <span className={`flex items-center gap-2 text-xs font-bold ${st.title}`}>
                      <span aria-hidden="true" className={`flex size-4 shrink-0 items-center justify-center rounded-full border-2 ${st.ring}`}>
                        {active && <span className={`size-2 rounded-full ${st.dot}`} />}
                      </span>
                      {item.title}
                    </span>
                    <span className="mt-1 block pl-6 text-xs leading-snug text-foreground/80">{item.desc}</span>
                  </button>
                );
              })}
            </div>

            <button
              type="button"
              onClick={() => onAskAI && onAskAI(hintLevel)}
              disabled={isAskingAI || isSubmitting}
              aria-busy={isAskingAI}
              className="mt-3 inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-full bg-purple-600 px-4 text-xs font-semibold text-white transition-all shadow-soft active:scale-95 hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
            >
              {isAskingAI ? (
                <>
                  <span aria-hidden="true" className="size-4 animate-spin rounded-full border-2 border-current/30 border-t-current" />
                  Đang xin gợi ý Mức {hintLevel}…
                </>
              ) : (
                <>
                  <Sparkles aria-hidden="true" className="size-4" />
                  Nhận gợi ý Mức {hintLevel}
                </>
              )}
            </button>
          </fieldset>
        )}

        {/* Section 2: Code Structure Recognition Card (Collapsible) */}
        {astAnalysis && (
          <div className="overflow-hidden rounded-lg border border-info-line bg-info-soft/50">
            <button
              type="button"
              onClick={() => setIsAstOpen(!isAstOpen)}
              aria-expanded={isAstOpen}
              className="flex w-full items-center justify-between gap-2 p-3 text-left text-sm font-bold text-info-strong transition-colors hover:bg-info-soft"
            >
              <span className="flex items-center gap-2">
                <Code aria-hidden="true" className="size-4" />
                Nhận diện nhanh code của bạn
              </span>
              <span className="flex items-center gap-2">
                <Badge variant={astAnalysis.valid ? 'success' : 'danger'}>{astAnalysis.valid ? 'Hợp lệ' : 'Có lỗi cú pháp'}</Badge>
                {isAstOpen ? <ChevronUp aria-hidden="true" className="size-4" /> : <ChevronDown aria-hidden="true" className="size-4" />}
              </span>
            </button>

            {isAstOpen && (
              <div className="space-y-2 border-t border-info-line p-3">
                <div className="grid grid-cols-2 gap-2 text-[0.8125rem]">
                  <div className="rounded-md bg-surface p-2">
                    <span className="block text-muted">Độ dài</span>
                    <span className="font-bold">{astAnalysis.line_count} dòng lệnh</span>
                  </div>
                  <div className="rounded-md bg-surface p-2">
                    <span className="block text-muted">Vòng lặp</span>
                    <span className="font-bold">
                      {astAnalysis.has_loops ? `Có dùng (${[astAnalysis.loop_details?.for_count ? 'for' : '', astAnalysis.loop_details?.while_count ? 'while' : ''].filter(Boolean).join(', ') || 'vòng lặp'})` : 'Chưa dùng'}
                    </span>
                  </div>
                  <div className="rounded-md bg-surface p-2">
                    <span className="block text-muted">Biến cộng dồn</span>
                    <span className="font-bold">{astAnalysis.has_accumulator ? 'Có' : 'Chưa có'}</span>
                  </div>
                  <div className="rounded-md bg-surface p-2">
                    <span className="block text-muted">Đệ quy</span>
                    <span className="font-bold">{astAnalysis.has_recursion ? 'Có' : 'Không'}</span>
                  </div>
                </div>

                {astAnalysis.structural_summary && (
                  <p className="rounded-md bg-surface p-2 text-[0.8125rem] text-muted">
                    {astAnalysis.structural_summary}
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Thẻ Gamification & Nút Thử thách Tối ưu Code Pythonic (Khi pass 100%) */}
        {testResults?.all_passed && (
          <div className="space-y-3 rounded-xl border border-success-line bg-success-soft p-3.5">
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0">
                <h4 className="text-sm font-bold text-success-strong">Đã vượt qua toàn bộ kiểm thử</h4>
                <p className="text-[0.8125rem] text-foreground">
                  {officialStars != null
                    ? `Điểm nỗ lực lượt nộp này: ${officialStars}/3`
                    : 'Điểm nỗ lực chỉ được ghi nhận khi bạn bấm "Nộp bài".'}
                </p>
              </div>
              {officialStars != null && (
                <div className="flex shrink-0 items-center gap-0.5" role="img" aria-label={`${officialStars} trên 3 điểm nỗ lực`}>
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Star key={i} aria-hidden="true" className={`size-6 ${i < officialStars ? 'fill-warning text-warning' : 'text-warning-line'}`} />
                  ))}
                </div>
              )}
            </div>

            {/* v5.3 (S2): thẻ lý do sao — minh bạch quy tắc, dữ liệu đã dùng và cách đạt mức cao hơn */}
            {starRationale && (
              <div className="space-y-2 rounded-lg border border-border bg-surface p-3 text-[0.8125rem] leading-relaxed">
                <p className="font-bold">Vì sao bạn nhận {officialStars} sao?</p>
                {starRationale.explanation && <p className="text-foreground">{starRationale.explanation}</p>}
                <dl className="grid grid-cols-2 gap-2">
                  <div className="rounded-md bg-warning-soft p-2">
                    <dt className="text-warning-strong">Mức gợi ý cao nhất</dt>
                    <dd className="font-bold text-warning-strong">Mức {starRationale.max_hint_level_used ?? '—'}</dd>
                  </div>
                  <div className="rounded-md bg-info-soft p-2">
                    <dt className="text-info-strong">Số lần nộp bài</dt>
                    <dd className="font-bold text-info-strong">{starRationale.attempt_count ?? '—'}</dd>
                  </div>
                </dl>
                {starRationale.how_to_improve && (
                  <p>
                    <span className="font-bold text-success-strong">Bước kế tiếp: </span>
                    {starRationale.how_to_improve}
                  </p>
                )}
                {Array.isArray(starRationale.rule) && starRationale.rule.length > 0 && (
                  <div>
                    <button
                      type="button"
                      onClick={() => setIsStarRuleOpen((open) => !open)}
                      aria-expanded={isStarRuleOpen}
                      className="flex min-h-9 items-center gap-1 rounded font-semibold text-info-strong hover:underline"
                    >
                      {isStarRuleOpen ? <ChevronUp aria-hidden="true" className="size-4" /> : <ChevronDown aria-hidden="true" className="size-4" />}
                      <span>Quy tắc tính sao</span>
                    </button>
                    {isStarRuleOpen && (
                      <ul className="mt-1.5 space-y-1">
                        {starRationale.rule.map((item) => (
                          <li key={item.stars} className={`flex items-start gap-2 ${item.stars === officialStars ? 'font-bold text-foreground' : 'text-muted'}`}>
                            <span className="shrink-0 font-mono font-bold text-warning-strong">{item.stars}★</span>
                            <span>{item.condition}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
                {starRationale.note && <p className="border-t border-border pt-2 text-muted">{starRationale.note}</p>}
              </div>
            )}

            {onOpenPythonicReview && (
              <button
                onClick={onOpenPythonicReview}
                type="button"
                className="inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-lg bg-ai px-3 text-sm font-semibold text-on-solid transition-colors hover:bg-ai/85"
              >
                <Sparkles aria-hidden="true" className="size-4" />
                <span>Thử thách tối ưu code Pythonic</span>
              </button>
            )}
          </div>
        )}

        {/* Section 3: AI Tutor Response Card */}
        <div>
          <h3 className="mb-2 text-sm font-bold">Gợi ý hướng giải</h3>

          {isAskingAI || (isSubmitting && !testResults?.all_passed) ? (
            <div role="status" className="flex flex-col items-center justify-center space-y-2 rounded-lg border border-ai-line bg-ai-soft p-6 text-center">
              <span aria-hidden="true" className="size-6 animate-spin rounded-full border-2 border-ai-line border-t-ai" />
              <p className="text-sm font-semibold text-ai-strong">Trợ lý AI đang phân tích bài giải của bạn…</p>
              <p className="text-[0.8125rem] text-muted">Đang chuẩn bị gợi ý Mức {hintLevel} phù hợp nhất với bài làm hiện tại</p>
            </div>
          ) : tutorHint ? (
            <div
              className={`space-y-3 rounded-xl border p-3.5 text-sm leading-relaxed ${
                testResults?.all_passed
                  ? 'border-success-line bg-success-soft'
                  : 'border-ai-line bg-ai-soft'
              }`}
            >
              <div className="max-w-none space-y-2 text-foreground">
                {formatHintText(tutorHint, {
                  canInsert: hintLevel === 3 && !testResults?.all_passed && Boolean(onInsertSkeleton),
                  onInsert: onInsertSkeleton,
                })}
                {canUndoInsert && onUndoInsert && (
                  <button
                    type="button"
                    onClick={onUndoInsert}
                    className="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-border bg-surface px-3 text-[0.8125rem] font-semibold text-foreground hover:border-primary"
                  >
                    <Undo2 aria-hidden="true" className="size-4" />
                    Hoàn tác, trả lại code cũ
                  </button>
                )}
              </div>
              {adaptiveStrategy && !testResults?.all_passed && (
                <div className="border-t border-ai-line pt-2 text-[0.8125rem] text-muted" aria-label="Vì sao nhận gợi ý này">
                  <p>
                    Vì sao nhận gợi ý này: {adaptiveStrategy.adaptation_codes?.includes('no_code_yet') ? 'bạn chưa viết dòng code nào nên gợi ý giúp hiểu đề và chọn bước đầu tiên' : adaptiveStrategy.adaptation_codes?.includes('concept_recurring_difficulty') ? 'có kiểm thử chưa đạt, và bạn đang vướng ở một phần kiến thức liên quan từ các bài trước'
                      : adaptiveStrategy.reason_code === 'recurring_difficulty' ? 'lịch sử cho thấy bạn đã thử bài này nhiều lần' : adaptiveStrategy.reason_code === 'failed_case_diagnosis' ? 'có kiểm thử chưa đạt để làm căn cứ phân tích' : 'chưa có đủ dữ liệu lịch sử nên bắt đầu bằng gợi mở an toàn'}.
                  </p>
                  {Array.isArray(adaptiveStrategy.adaptations) && adaptiveStrategy.adaptations.length > 0 && (
                    <ul className="mt-1 space-y-1.5">
                      {adaptiveStrategy.adaptations.map((a) => (
                        <li key={a.code}>
                          <span>· {a.reason_vi}</span>
                          {a.concept_label_vi && (
                            <span className="ml-1.5 inline-block rounded-full border border-ai-line px-2 py-0.5 text-xs font-medium text-foreground">
                              Phần kiến thức: {a.concept_label_vi}{a.concept_state_label_vi ? ` · ${a.concept_state_label_vi}` : ''}
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {/* Nút leo thang gợi ý thân thiện */}
              {tutorHint && !testResults?.all_passed && hintLevel < 3 && (
                <button
                  type="button"
                  onClick={() => {
                    const nextLevel = hintLevel + 1;
                    setHintLevel(nextLevel);
                    if (onAskAI) onAskAI(nextLevel);
                    else if (onEscalate) onEscalate(nextLevel);
                  }}
                  disabled={isAskingAI || isSubmitting}
                  className="mt-1 flex min-h-10 w-full items-center justify-center gap-1.5 rounded-lg border border-warning-line bg-warning-soft px-3 text-sm font-semibold text-warning-strong transition-colors hover:border-warning disabled:cursor-not-allowed disabled:opacity-55"
                >
                  <span>Vẫn thấy khó? Xem gợi ý chi tiết hơn (Mức {hintLevel + 1})</span>
                  <ChevronRight aria-hidden="true" className="size-4 shrink-0" />
                </button>
              )}

              {/* v5.3 (S1.2): đánh giá gợi ý ask_ai; lượt nộp đã pass dùng lời chúc tất định nên không có interaction để đánh giá */}
              <TutorFeedbackButtons
                interactionId={hintInteractionId}
                prompt="Gợi ý này có giúp bạn không?"
                className="border-t border-ai-line pt-2"
              />

              <div className="flex items-center justify-between gap-2 border-t border-ai-line pt-2 text-[0.8125rem] text-muted">
                <span>{getLlmBadgeLabel(llmSource)}</span>
                <span className="text-right">Dựa trên kết quả chạy thực tế & phân tích code</span>
              </div>
            </div>
          ) : (
            <div className="space-y-2 rounded-xl border-2 border-dashed border-ai-line bg-ai-soft/40 p-6 text-center">
              <HelpCircle aria-hidden="true" className="mx-auto size-8 text-ai" />
              <p className="text-sm font-bold">Chưa có gợi ý từ Gia sư AI.</p>
              <p className="text-[0.8125rem] leading-normal text-muted">
                Hãy viết code và bấm <span className="font-bold text-info-strong">“Chạy thử”</span> hoặc <span className="font-bold text-ai-strong">“Hỏi gia sư AI”</span> để nhận hướng dẫn.
              </p>
            </div>
          )}
        </div>

        {/* Section 4: Multi-turn Chat với Gia sư AI (Phase 8) */}
        {/* Mở sẵn từ khi vào bài (hỏi khái niệm không cần xin gợi ý trước); chỉ khóa ô nhập ở chế độ kỳ thi. */}
        {(
          <div className="space-y-2.5 border-t border-border pt-4">
            <div className="flex items-center justify-between text-sm font-bold">
              <span className="flex items-center gap-1.5 text-info-strong">
                <MessageSquare aria-hidden="true" className="size-4" />
                <span>{isCodeChatUnlocked ? 'Trò chuyện về bài đã nộp' : 'Hỏi khái niệm Python'}</span>
              </span>
              {chatMessages.length > 0 && (
                <span className="rounded-full bg-info-soft px-2 py-0.5 font-mono text-[0.8125rem] font-semibold text-info-strong">
                  {chatMessages.length} tin nhắn
                </span>
              )}
            </div>

            {/* Chat History Bubbles */}
            <div className="max-h-64 space-y-3 overflow-y-auto pr-1.5 text-sm leading-relaxed" aria-live="polite" aria-relevant="additions text">
              {chatMessages.length === 0 ? (
                <div className="flex items-start gap-2.5 rounded-xl border border-info-line bg-info-soft p-3">
                  <MessageSquare className="mt-0.5 size-4 shrink-0 text-info-strong" aria-hidden="true" />
                  {isCodeChatUnlocked ? (
                    <p className="text-[0.8125rem] leading-relaxed">Bạn đã nộp bài đạt. Giờ bạn có thể hỏi chi tiết về code đã nộp: vì sao nó chạy đúng, từng dòng làm gì, hay cách viết khác.</p>
                  ) : (
                    <p className="text-[0.8125rem] leading-relaxed">
                      Khung này giải thích <strong className="font-bold">khái niệm Python tổng quát</strong> và luật Điểm nỗ lực; Gia sư không xem code bài đang làm ở đây. Cần gỡ lỗi bài làm, hãy bấm <strong className="font-bold text-ai-strong">Hỏi gia sư AI</strong>. Sau khi <strong className="font-bold">Nộp bài</strong> đạt, bạn hỏi được chi tiết về code đã nộp.
                    </p>
                  )}
                </div>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex flex-col ${
                      msg.role === 'user' ? 'items-end' : 'items-start'
                    }`}
                  >
                    <span className={`mb-1 px-1 text-[0.8125rem] font-semibold ${msg.role === 'user' ? 'text-info-strong' : 'text-ai-strong'}`}>
                      {msg.role === 'user' ? 'Bạn' : 'Gia sư PyTutor'}
                    </span>
                    <div
                      className={`max-w-[90%] rounded-2xl p-3 leading-relaxed ${
                        msg.role === 'user'
                          ? 'rounded-br-sm bg-slate-950 text-white dark:bg-emerald-500 dark:text-white shadow-soft'
                          : 'rounded-bl-sm border border-border/80 bg-surface-raised text-foreground shadow-soft'
                      } whitespace-pre-wrap break-words text-xs`}
                    >
                      {renderBold(msg.content)}
                    </div>
                    {/* v5.3 (S1.3): nguồn tài liệu nội bộ đã dùng, hoặc nói rõ là không có nguồn phù hợp */}
                    {msg.role === 'assistant' && msg.knowledgeStatus === 'grounded' && msg.sources?.length > 0 && (
                      <div className="mt-1 max-w-[92%] px-1 text-[0.8125rem] leading-snug text-muted">
                        {/* v5.5: gọi đúng tên — đây là tài liệu đã đưa cho gia sư khi trả lời, chưa chắc câu trả lời đã trích nó */}
                        <span className="font-semibold text-foreground">Tài liệu nội bộ liên quan: </span>
                        {msg.sources.map((src, sIdx) => (
                          <span key={`${src.source}-${src.section}-${sIdx}`}>
                            {sIdx > 0 && '; '}
                            {src.section ? `mục “${src.section}”` : 'tài liệu'} <span className="font-mono">({src.source})</span>
                            {src.origin === 'class' && <span className="font-semibold text-success-strong"> — do giảng viên lớp cung cấp</span>}
                          </span>
                        ))}
                        {msg.sources.some((src) => src.origin !== 'class') && (
                          <span className="block">Tài liệu do PyTutor biên soạn, chưa phải giáo trình chính thức của NEU.</span>
                        )}
                        <span className="block">Gia sư được cung cấp các mục này khi trả lời. Nếu câu trả lời không nhắc tới chúng, bạn nên tự đọc mục đó để đối chiếu.</span>
                      </div>
                    )}
                    {msg.role === 'assistant' && msg.knowledgeStatus === 'no_source' && (
                      <p className="mt-1 max-w-[92%] px-1 text-[0.8125rem] leading-snug text-muted">
                        Không có tài liệu nội bộ phù hợp với câu hỏi này, nên câu trả lời không kèm nguồn. Bạn nên đối chiếu thêm với giáo trình hoặc giảng viên.
                      </p>
                    )}
                    {msg.role === 'assistant' && (
                      <TutorFeedbackButtons interactionId={msg.interactionId} className="mt-1 px-1" />
                    )}
                  </div>
                ))
              )}

              {isSendingChat && (
                <div className="flex items-center gap-2 rounded-2xl bg-surface-raised border border-border/80 p-3 text-xs" role="status">
                  <span className="size-3.5 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" aria-hidden="true" />
                  <span className="font-semibold text-foreground">Gia sư đang soạn câu trả lời…</span>
                </div>
              )}
            </div>

            {/* Chat Input Form */}
            <form onSubmit={handleSendChat} className="mt-2 relative flex items-center">
              <input
                type="text"
                aria-label="Câu hỏi gửi Gia sư PyTutor"
                value={userQuestion}
                onChange={(e) => setUserQuestion(e.target.value)}
                placeholder={isExamMode ? "Gia sư AI bị khóa trong chế độ kỳ thi..." : (isCodeChatUnlocked ? "Hỏi về code đã nộp..." : "Hỏi một khái niệm Python...")}
                disabled={isSendingChat || isExamMode}
                className="min-h-11 w-full rounded-full border border-border/80 bg-surface pl-4 pr-12 text-xs text-foreground placeholder:text-muted/60 outline-none shadow-soft focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-55"
              />
              <button
                type="submit"
                disabled={isSendingChat || !userQuestion.trim() || isExamMode}
                aria-label={isSendingChat ? 'Đang gửi câu hỏi' : 'Gửi câu hỏi tới Gia sư AI'}
                className="absolute right-1.5 size-8 rounded-full bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 text-white flex items-center justify-center transition-all active:scale-95 cursor-pointer shadow-soft"
                title={isExamMode ? "Gia sư AI bị khóa trong Chế độ Kỳ thi" : "Gửi câu hỏi tới Gia sư AI"}
              >
                <Send aria-hidden="true" className="size-3.5" />
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

function HintCodeBlock({ codeBody, canInsert, onInsert }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(codeBody);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      alert('Không sao chép được. Hãy bôi đen đoạn code rồi nhấn Ctrl+C.');
    }
  };
  const btn = 'inline-flex min-h-8 items-center gap-1.5 rounded-md border border-border bg-surface-raised px-2.5 text-[0.8125rem] font-semibold text-foreground hover:border-primary';
  return (
    <div className="my-2">
      <pre className="overflow-x-auto rounded-t-lg border border-border bg-surface p-2.5 font-mono text-[0.8125rem] text-success-strong">
        <code>{codeBody}</code>
      </pre>
      <div className="flex flex-wrap items-center justify-end gap-2 rounded-b-lg border border-t-0 border-border bg-surface-raised p-1.5">
        <button type="button" onClick={copy} className={btn} aria-live="polite">
          {copied ? <Check aria-hidden="true" className="size-4" /> : <Copy aria-hidden="true" className="size-4" />}
          {copied ? 'Đã chép' : 'Sao chép'}
        </button>
        {canInsert && /TODO/.test(codeBody) && (
          <button type="button" onClick={() => onInsert(codeBody)} className={btn}>
            <FileInput aria-hidden="true" className="size-4" />
            Dán vào editor
          </button>
        )}
      </div>
    </div>
  );
}

// Bảng Markdown trong gợi ý (Mức 3: "bảng chạy tay" để trống). Ô trống giữ chiều cao để người học nhìn thấy chỗ cần tự điền.
function HintTable({ rows }) {
  const { header, body } = parseTable(rows);
  const cell = 'border border-border px-2 py-1 align-top';
  return (
    <div className="my-2 overflow-x-auto rounded-lg border border-border">
      <table className="w-full min-w-max border-collapse text-left text-[0.8125rem]">
        {header && (
          <thead className="bg-surface-raised">
            <tr>
              {header.map((h, i) => (
                <th key={i} scope="col" className={`${cell} font-semibold text-foreground`}>{renderBold(h)}</th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {body.map((r, ri) => (
            <tr key={ri}>
              {r.map((c, ci) => (
                <td key={ci} className={`${cell} ${c ? 'text-foreground' : 'h-8 min-w-[3.5rem] bg-surface'}`}>{c ? renderBold(c) : null}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatHintText(text, { canInsert = false, onInsert = null } = {}) {
  if (!text) return null;

  const parts = text.split(/(```[\s\S]*?```)/g);

  return parts.map((part, pIdx) => {
    if (part.startsWith('```') && part.endsWith('```')) {
      const lines = part.slice(3, -3).trim().split('\n');
      const lang = lines[0].trim().startsWith('python') ? 'python' : '';
      const codeBody = lang ? lines.slice(1).join('\n') : lines.join('\n');

      return <HintCodeBlock key={pIdx} codeBody={codeBody} canInsert={canInsert} onInsert={onInsert} />;
    }

    const paragraphs = part.split('\n\n');
    return paragraphs.map((para, paraIdx) => {
      const lines = para.split('\n');
      return (
        <div key={`${pIdx}-${paraIdx}`} className="space-y-1">
          {groupTableLines(lines).map((item, lIdx) => {
            if (item.table) return <HintTable key={lIdx} rows={item.table} />;
            const content = item.line.trim();
            if (!content) return null;

            if (content.startsWith('# ')) {
              return (
                <h3 key={lIdx} className="mb-1 mt-2 text-base font-bold text-ai-strong">
                  {content.replace('# ', '')}
                </h3>
              );
            }
            if (content.startsWith('## ')) {
              return (
                <h4 key={lIdx} className="mb-1 mt-2 text-sm font-bold text-ai-strong">
                  {content.replace('## ', '')}
                </h4>
              );
            }
            if (content.startsWith('### ')) {
              return (
                <h5 key={lIdx} className="mb-0.5 mt-1.5 text-sm font-bold text-ai-strong">
                  {content.replace('### ', '')}
                </h5>
              );
            }
            if (content.startsWith('- ') || content.startsWith('* ')) {
              return (
                <div key={lIdx} className="ml-1 flex items-start gap-2 text-foreground">
                  <span aria-hidden="true" className="font-bold text-ai-strong">•</span>
                  <span>{renderBold(content.replace(/^[-*]\s+/, ''))}</span>
                </div>
              );
            }
            const numMatch = content.match(/^(\d+)\.\s+(.*)/);
            if (numMatch) {
              return (
                <div key={lIdx} className="ml-1 flex items-start gap-2 text-foreground">
                  <span className="font-mono font-bold text-info-strong">{numMatch[1]}.</span>
                  <span>{renderBold(numMatch[2])}</span>
                </div>
              );
            }

            return (
              <p key={lIdx} className="leading-relaxed">
                {renderBold(content)}
              </p>
            );
          })}
        </div>
      );
    });
  });
}

function renderBold(str) {
  if (!str) return null;
  const parts = str.split(/(\*\*.*?\*\*|\`.*?\`|(?<![\w*])\*[^*\s][^*]*\*(?![\w*]))/g);
  return parts.map((part, i) => {
    if (part.length > 2 && part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
      return <em key={i} className="italic text-muted">{part.slice(1, -1)}</em>;
    }
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-foreground">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="rounded border border-ai-line bg-surface px-1 py-0.5 font-mono text-[0.8125rem] text-ai-strong">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
