import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, Plus, Trash2, Code2, BookOpen, CheckCircle } from 'lucide-react';
import Header from '../components/Header';
import { Input } from '../components/ui';
import { fetchExerciseDetail, createInstructorExercise, updateInstructorExercise, fetchKnowledgeComponents } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ExerciseFormPage() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const navigate = useNavigate();
  const { isInstructor, user } = useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  // Form States
  const [exerciseId, setExerciseId] = useState('');
  const [title, setTitle] = useState('');
  const [difficulty, setDifficulty] = useState('Dễ');
  const [category, setCategory] = useState('');
  const [kcTags, setKcTags] = useState([]); // năng lực giảng viên chọn (không gồm io_format, luôn có)
  const [kcOptions, setKcOptions] = useState([]);
  const [kcOptionsLoaded, setKcOptionsLoaded] = useState(false);
  const [savedKcTags, setSavedKcTags] = useState(null); // mã đã lưu của bài; chỉ giữ mã còn bật khi đã biết danh sách năng lực
  const [description, setDescription] = useState('');
  const [starterCode, setStarterCode] = useState('# Viết code Python của bạn ở đây...\n');
  const [algorithmNotes, setAlgorithmNotes] = useState('');
  const [testCases, setTestCases] = useState([
    { input: '1\n', expected_output: '1', description: 'Trường hợp mẫu 1' },
    { input: '5\n', expected_output: '15', description: 'Trường hợp mẫu 2' },
  ]);

  // Bảo vệ route: Chỉ giảng viên mới vào được
  useEffect(() => {
    if (!isInstructor && user) {
      navigate('/');
    }
  }, [isInstructor, user, navigate]);

  useEffect(() => {
    let alive = true;
    fetchKnowledgeComponents()
      .then((items) => { if (alive) { setKcOptions((items || []).filter((k) => k.is_active !== false)); setKcOptionsLoaded(true); } })
      .catch(() => { if (alive) { setKcOptions([]); setKcOptionsLoaded(true); } });
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    const initPage = async () => {

      if (isEditMode) {
        setIsLoading(true);
        try {
          const detail = await fetchExerciseDetail(id);
          setExerciseId(detail.id);
          setTitle(detail.title);
          setDifficulty(detail.difficulty);
          setCategory(detail.category);
          setSavedKcTags((detail.kc_tags || []).filter((k) => k !== 'io_format'));
          setDescription(detail.description);
          setStarterCode(detail.starter_code || '');
          setAlgorithmNotes(detail.algorithm_notes || '');
          setTestCases(detail.test_cases || []);
        } catch (err) {
          console.error('Lỗi khi tải chi tiết bài tập:', err);
          setError('Không thể tải thông tin bài tập cần chỉnh sửa.');
        } finally {
          setIsLoading(false);
        }
      }
    };

    initPage();
  }, [id, isEditMode]);

  // Chỉ giữ các mã năng lực còn bật: mã đã bị tắt/xóa không hiện ra nên không bỏ chọn được, và sẽ làm lệch kiểm tra "ít nhất một năng lực".
  useEffect(() => {
    if (savedKcTags === null || !kcOptionsLoaded) return;
    const active = new Set(kcOptions.map((k) => k.kc));
    setKcTags(savedKcTags.filter((k) => active.has(k)));
  }, [savedKcTags, kcOptions, kcOptionsLoaded]);

  // Thêm test case mới
  const handleAddTestCase = () => {
    setTestCases([
      ...testCases,
      { input: '', expected_output: '', description: `Test case #${testCases.length + 1}` }
    ]);
  };

  // Cập nhật test case
  const handleTestCaseChange = (index, field, value) => {
    const updated = [...testCases];
    updated[index][field] = value;
    setTestCases(updated);
  };

  // Xóa test case
  const handleRemoveTestCase = (index) => {
    if (testCases.length <= 1) {
      alert('Bài tập cần có ít nhất 1 test case để kiểm thử.');
      return;
    }
    setTestCases(testCases.filter((_, i) => i !== index));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    const nextFieldErrors = {
      ...(!exerciseId.trim() && { exerciseId: 'Vui lòng nhập mã bài tập.' }),
      ...(!title.trim() && { title: 'Vui lòng nhập tiêu đề bài tập.' }),
      ...(!description.trim() && { description: 'Vui lòng nhập mô tả đề bài.' }),
      ...(!category.trim() && { category: 'Vui lòng nhập chủ đề của bài.' }),
      ...(kcTags.length === 0 && { kcTags: 'Hãy chọn ít nhất một năng lực mà bài này rèn luyện.' }),
    };
    setFieldErrors(nextFieldErrors);
    if (Object.keys(nextFieldErrors).length > 0) {
      setError('Hãy kiểm tra các trường được đánh dấu trước khi lưu.');
      return;
    }

    // Format input của test cases có newline nếu cần
    const formattedTestCases = testCases.map(tc => ({
      input: tc.input.endsWith('\n') ? tc.input : `${tc.input}\n`,
      expected_output: tc.expected_output.trim(),
      description: tc.description.trim() || 'Test case'
    }));

    const payload = {
      id: exerciseId.trim(),
      title: title.trim(),
      difficulty,
      category: category.trim(),
      description,
      starter_code: starterCode,
      algorithm_notes: algorithmNotes,
      kc_tags: kcTags,
      test_cases: formattedTestCases
    };

    setIsLoading(true);
    try {
      if (isEditMode) {
        await updateInstructorExercise(exerciseId, payload);
        alert('Đã cập nhật bài tập thành công!');
      } else {
        await createInstructorExercise(payload);
        alert('Đã tạo bài tập mới thành công vào ngân hàng đề!');
      }
      navigate('/instructor');
    } catch (err) {
      console.error('Lỗi khi lưu bài tập:', err);
      setError(err.response?.data?.detail || 'Có lỗi xảy ra khi lưu bài tập vào cơ sở dữ liệu.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-canvas font-sans text-foreground overflow-hidden">
      <Header
      />

      <main className="flex-1 overflow-y-auto p-4 sm:p-6 pb-20 max-w-5xl w-full mx-auto space-y-6">
        {/* Top Navigation */}
        <div className="flex items-center justify-between">
          <Link
            to="/instructor"
            className="flex items-center space-x-1.5 text-xs text-muted hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Quay lại Dashboard Giảng viên</span>
          </Link>

          <h2 className="text-base sm:text-lg font-bold text-foreground">
            {isEditMode ? `Chỉnh sửa: ${title}` : 'Thêm bài tập lập trình mới'}
          </h2>
        </div>

        {error && (
          <div role="alert" className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-300 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Section 1: Thông tin cơ bản */}
          <div className="bg-surface border border-border p-5 rounded-2xl space-y-4 shadow-soft">
            <h3 className="text-xs font-semibold text-muted uppercase tracking-wider flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-emerald-500" />
              <span>1. THÔNG TIN BÀI TẬP</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Mã bài tập (Unique ID) *"
                type="text"
                value={exerciseId}
                onChange={(e) => { setExerciseId(e.target.value); setError(''); setFieldErrors(prev => ({ ...prev, exerciseId: undefined })); }}
                disabled={isEditMode}
                placeholder="ví dụ: ex_06_fibonacci"
                error={fieldErrors.exerciseId}
                aria-required="true"
                className="font-mono"
              />

              <Input
                label="Tiêu đề bài tập *"
                type="text"
                value={title}
                onChange={(e) => { setTitle(e.target.value); setError(''); setFieldErrors(prev => ({ ...prev, title: undefined })); }}
                placeholder="ví dụ: Bài 06: Dãy số Fibonacci"
                error={fieldErrors.title}
                aria-required="true"
              />

              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  Độ khó
                </label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full min-h-11 bg-surface border border-border rounded-xl px-3 py-2 text-sm text-foreground outline-none transition-colors duration-200 focus-visible:border-emerald-500 focus-visible:ring-2 focus-visible:ring-emerald-500/25"
                >
                  <option value="Dễ">Dễ</option>
                  <option value="Trung bình">Trung bình</option>
                  <option value="Khó">Khó</option>
                </select>
              </div>

              <Input
                label="Chủ đề thuật toán (Category) *"
                type="text"
                value={category}
                onChange={(e) => { setCategory(e.target.value); setError(''); setFieldErrors(prev => ({ ...prev, category: undefined })); }}
                placeholder="Chưa chọn — ví dụ: Đếm tần suất trong danh sách"
                error={fieldErrors.category}
                aria-required="true"
              />
            </div>

            <fieldset className="space-y-2 rounded-xl border border-border p-3.5" aria-describedby="kc-tags-hint">
              <legend className="px-1 text-xs font-medium text-foreground">Năng lực của bài *</legend>
              <p id="kc-tags-hint" className="text-xs text-muted">
                Năng lực quyết định bài này được tính vào phần nào trong hồ sơ học tập của sinh viên. "Nhập/xuất và định dạng" luôn có ở mọi bài.
                Thiếu năng lực phù hợp? Thêm ở mục "Đơn vị kiến thức (KCs)" trong Ngân hàng bài tập.
              </p>
              <div className="flex flex-wrap gap-2">
                {kcOptions.length === 0 && <span className="text-xs text-muted">Đang tải danh sách năng lực...</span>}
                {kcOptions.map((k) => {
                  const fixed = k.kc === 'io_format';
                  const checked = fixed || kcTags.includes(k.kc);
                  return (
                    <label key={k.kc} className={`inline-flex min-h-9 items-center gap-2 rounded-xl border px-3 text-xs ${checked ? 'border-emerald-500/50 bg-emerald-500/10 text-foreground' : 'border-border bg-surface text-muted'} ${fixed ? 'opacity-80' : 'cursor-pointer'}`}>
                      <input
                        type="checkbox"
                        checked={checked}
                        disabled={fixed}
                        onChange={(e) => {
                          setKcTags((prev) => (e.target.checked ? [...prev, k.kc] : prev.filter((x) => x !== k.kc)));
                          setError('');
                          setFieldErrors((prev) => ({ ...prev, kcTags: undefined }));
                        }}
                        className="size-4 rounded border-border accent-emerald-600"
                      />
                      <span>{k.label_vi}</span>
                    </label>
                  );
                })}
              </div>
              {fieldErrors.kcTags && <p role="alert" className="text-xs font-medium text-rose-500">{fieldErrors.kcTags}</p>}
            </fieldset>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2" htmlFor="exercise-description">
                Mô tả đề bài & Ví dụ (Hỗ trợ Markdown) *
              </label>
              <textarea
                id="exercise-description"
                value={description}
                onChange={(e) => { setDescription(e.target.value); setError(''); setFieldErrors(prev => ({ ...prev, description: undefined })); }}
                rows={6}
                placeholder="### Mô tả bài toán&#10;Viết chương trình...&#10;&#10;### Đầu vào (Input):&#10;Một số nguyên n...&#10;&#10;### Đầu ra (Output):&#10;Kết quả..."
                aria-invalid={fieldErrors.description ? 'true' : undefined}
                aria-describedby={fieldErrors.description ? 'exercise-description-error' : undefined}
                aria-required="true"
                className="w-full rounded-xl border border-border bg-surface p-3 text-sm text-foreground placeholder:text-muted outline-none transition-colors duration-200 focus-visible:border-emerald-500 focus-visible:ring-2 focus-visible:ring-emerald-500/25 font-mono leading-relaxed"
              />
              {fieldErrors.description && <p id="exercise-description-error" role="alert" className="mt-2 text-sm text-rose-500">{fieldErrors.description}</p>}
            </div>
          </div>

          {/* Section 2: Code mẫu ban đầu */}
          <div className="bg-surface border border-border p-5 rounded-2xl space-y-4 shadow-soft">
            <h3 className="text-xs font-semibold text-muted uppercase tracking-wider flex items-center space-x-2">
              <Code2 className="w-4 h-4 text-sky-500" />
              <span>2. CODE MẪU KHỞI TẠO CHO HỌC VIÊN (STARTER CODE)</span>
            </h3>

            <textarea
              value={starterCode}
              onChange={(e) => setStarterCode(e.target.value)}
              rows={4}
              className="w-full rounded-xl border border-border bg-surface p-3 text-sm text-emerald-700 dark:text-emerald-300 font-mono leading-relaxed outline-none transition-colors duration-200 focus-visible:border-emerald-500 focus-visible:ring-2 focus-visible:ring-emerald-500/25"
            />
          </div>

          {/* Ý tưởng thuật toán (tùy chọn, chỉ dùng cho gợi ý Mức 3, sinh viên không thấy) */}
          <div className="bg-surface border border-border p-5 rounded-2xl space-y-3 shadow-soft">
            <h3 className="text-xs font-semibold text-muted uppercase tracking-wider">
              Ý TƯỞNG THUẬT TOÁN (TÙY CHỌN, CHỈ GIA SƯ AI DÙNG Ở GỢI Ý MỨC 3)
            </h3>
            <p className="text-xs text-muted">
              Viết bằng lời các bước giải, không viết mã Python. Sinh viên không thấy ô này; chỉ gợi ý Mức 3 dùng nó để diễn đạt lại theo bài làm của từng em.
            </p>
            <textarea
              value={algorithmNotes}
              onChange={(e) => setAlgorithmNotes(e.target.value)}
              rows={4}
              maxLength={3000}
              placeholder="Ví dụ: Số nhỏ hơn 2 không phải số nguyên tố. Với n còn lại, thử lần lượt từng số từ 2 tới căn bậc hai của n; gặp một ước thì dừng và kết luận NO, thử hết mà không có ước thì YES."
              className="w-full rounded-xl border border-border bg-surface p-3 text-sm leading-relaxed outline-none transition-colors duration-200 focus-visible:border-emerald-500 focus-visible:ring-2 focus-visible:ring-emerald-500/25"
            />
          </div>

          {/* Section 3: Bộ kiểm thử (Test Cases) */}
          <div className="bg-surface border border-border p-5 rounded-2xl space-y-4 shadow-soft">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-muted uppercase tracking-wider flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-amber-500" />
                <span>3. BỘ TEST CASES CHUẨN (BỘ KIỂM THỬ DÙNG ĐỂ CHẤM)</span>
              </h3>
              <button
                type="button"
                onClick={handleAddTestCase}
                className="flex items-center space-x-1.5 py-1.5 px-3 rounded-xl bg-surface-raised hover:bg-surface text-xs text-foreground border border-border transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 shadow-soft"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Thêm Test Case</span>
              </button>
            </div>

            <div className="space-y-3">
              {testCases.map((tc, idx) => (
                <div key={idx} className="bg-surface-raised border border-border p-4 rounded-xl space-y-3 shadow-soft">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-foreground">Test Case #{idx + 1}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveTestCase(idx)}
                      className="text-muted hover:text-rose-500 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400 rounded"
                      title="Xóa test case này"
                      aria-label={`Xóa test case ${idx + 1}`}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 text-xs">
                    <div className="sm:col-span-5">
                      <Input
                        label="Dữ liệu vào (Input - stdin)"
                        type="text"
                        value={tc.input.replace(/\n$/, '')}
                        onChange={(e) => handleTestCaseChange(idx, 'input', e.target.value)}
                        placeholder="ví dụ: 5"
                        required
                        className="font-mono text-xs text-emerald-700 dark:text-emerald-300 placeholder:text-muted"
                      />
                    </div>
                    <div className="sm:col-span-4">
                      <Input
                        label="Kết quả kỳ vọng (Expected Output)"
                        type="text"
                        value={tc.expected_output}
                        onChange={(e) => handleTestCaseChange(idx, 'expected_output', e.target.value)}
                        placeholder="ví dụ: 15"
                        required
                        className="font-mono text-xs text-sky-700 dark:text-sky-300 placeholder:text-muted"
                      />
                    </div>
                    <div className="sm:col-span-3">
                      <Input
                        label="Mục đích kiểm thử"
                        type="text"
                        value={tc.description}
                        onChange={(e) => handleTestCaseChange(idx, 'description', e.target.value)}
                        placeholder="ví dụ: n = 5 thông thường"
                        className="text-xs placeholder:text-muted"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sticky Action Buttons Bar */}
          <div className="sticky bottom-0 bg-surface/95 backdrop-blur-md py-3.5 px-4 rounded-2xl border border-border flex items-center justify-between shadow-bento mt-6 z-10">
            <div className="text-xs text-muted flex items-center space-x-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
              <span>Đã cấu hình <b>{testCases.length}</b> trường hợp kiểm thử</span>
            </div>
            <div className="flex items-center space-x-3">
              <Link
                to="/instructor"
                className="py-2.5 px-4 rounded-xl bg-surface-raised hover:bg-surface text-foreground border border-border text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 shadow-soft"
              >
                Hủy bỏ
              </Link>
              <button
                type="submit"
                disabled={isLoading}
                className="flex items-center space-x-2 py-2.5 px-6 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-soft transition-all cursor-pointer disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300"
              >
                <Save className="w-4 h-4" />
                <span>{isLoading ? 'Đang lưu...' : 'Lưu bài tập vào hệ thống'}</span>
              </button>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
}
