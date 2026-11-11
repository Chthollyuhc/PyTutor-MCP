import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, Plus, Trash2, Code2, BookOpen, CheckCircle } from 'lucide-react';
import Header from '../components/Header';
import { Input } from '../components/ui';
import { checkHealth, fetchExerciseDetail, createInstructorExercise, updateInstructorExercise } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ExerciseFormPage() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const navigate = useNavigate();
  const { isInstructor, user } = useAuth();

  const [health, setHealth] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  // Form States
  const [exerciseId, setExerciseId] = useState('');
  const [title, setTitle] = useState('');
  const [difficulty, setDifficulty] = useState('Dễ');
  const [category, setCategory] = useState('Vòng lặp & Biến tích lũy');
  const [description, setDescription] = useState('');
  const [starterCode, setStarterCode] = useState('# Viết code Python của bạn ở đây...\n');
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
    const initPage = async () => {
      const hData = await checkHealth();
      setHealth(hData);

      if (isEditMode) {
        setIsLoading(true);
        try {
          const detail = await fetchExerciseDetail(id);
          setExerciseId(detail.id);
          setTitle(detail.title);
          setDifficulty(detail.difficulty);
          setCategory(detail.category);
          setDescription(detail.description);
          setStarterCode(detail.starter_code || '');
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
    <div className="h-screen w-screen flex flex-col bg-slate-950 font-sans text-slate-100 overflow-hidden">
      <Header
        health={health}
      />

      <main className="flex-1 overflow-y-auto p-4 sm:p-6 pb-20 max-w-5xl w-full mx-auto space-y-6">
        {/* Top Navigation */}
        <div className="flex items-center justify-between">
          <Link
            to="/instructor"
            className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Quay lại Dashboard Giảng viên</span>
          </Link>

          <h2 className="text-base sm:text-lg font-bold text-white">
            {isEditMode ? `Chỉnh sửa: ${title}` : 'Thêm bài tập lập trình mới'}
          </h2>
        </div>

        {error && (
          <div role="alert" className="p-3.5 rounded-xl bg-rose-950/50 border border-rose-400/30 text-rose-200 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Section 1: Thông tin cơ bản */}
          <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl space-y-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-emerald-400" />
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
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Độ khó
                </label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full min-h-11 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white outline-none transition-colors duration-200 focus-visible:border-emerald-400 focus-visible:ring-2 focus-visible:ring-emerald-400/25"
                >
                  <option value="Dễ">Dễ</option>
                  <option value="Trung bình">Trung bình</option>
                  <option value="Khó">Khó</option>
                </select>
              </div>

              <Input
                label="Chủ đề thuật toán (Category)"
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="ví dụ: Vòng lặp & Đệ quy"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2" htmlFor="exercise-description">
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
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-sm text-slate-100 placeholder:text-slate-400 outline-none transition-colors duration-200 focus-visible:border-emerald-400 focus-visible:ring-2 focus-visible:ring-emerald-400/25 font-mono leading-relaxed"
              />
              {fieldErrors.description && <p id="exercise-description-error" role="alert" className="mt-2 text-sm text-rose-200">{fieldErrors.description}</p>}
            </div>
          </div>

          {/* Section 2: Code mẫu ban đầu */}
          <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl space-y-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
              <Code2 className="w-4 h-4 text-cyan-400" />
              <span>2. CODE MẪU KHỞI TẠO CHO HỌC VIÊN (STARTER CODE)</span>
            </h3>

            <textarea
              value={starterCode}
              onChange={(e) => setStarterCode(e.target.value)}
              rows={4}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-sm text-emerald-200 font-mono leading-relaxed outline-none transition-colors duration-200 focus-visible:border-emerald-400 focus-visible:ring-2 focus-visible:ring-emerald-400/25"
            />
          </div>

          {/* Section 3: Bộ kiểm thử (Test Cases) */}
          <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-amber-400" />
                <span>3. BỘ TEST CASES CHUẨN (GROUND TRUTH CHO MCP SANDBOX)</span>
              </h3>
              <button
                type="button"
                onClick={handleAddTestCase}
                className="flex items-center space-x-1 py-1 px-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-emerald-200 border border-slate-700 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Thêm Test Case</span>
              </button>
            </div>

            <div className="space-y-3">
              {testCases.map((tc, idx) => (
                <div key={idx} className="bg-slate-950/80 border border-slate-800/80 p-3.5 rounded-xl space-y-2.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-300">Test Case #{idx + 1}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveTestCase(idx)}
                      className="text-slate-300 hover:text-rose-300 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400 rounded"
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
                        className="font-mono text-xs text-emerald-200 placeholder:text-slate-400"
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
                        className="font-mono text-xs text-cyan-200 placeholder:text-slate-400"
                      />
                    </div>
                    <div className="sm:col-span-3">
                      <Input
                        label="Mục đích kiểm thử"
                        type="text"
                        value={tc.description}
                        onChange={(e) => handleTestCaseChange(idx, 'description', e.target.value)}
                        placeholder="ví dụ: n = 5 thông thường"
                        className="text-xs placeholder:text-slate-400"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sticky Action Buttons Bar */}
          <div className="sticky bottom-0 bg-slate-950/95 backdrop-blur-md py-3.5 px-4 rounded-xl border border-slate-800 flex items-center justify-between shadow-2xl mt-6 z-10">
            <div className="text-xs text-slate-400 flex items-center space-x-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              <span>Đã cấu hình <b>{testCases.length}</b> trường hợp kiểm thử</span>
            </div>
            <div className="flex items-center space-x-3">
              <Link
                to="/instructor"
                className="py-2.5 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
              >
                Hủy bỏ
              </Link>
              <button
                type="submit"
                disabled={isLoading}
                className="flex items-center space-x-2 py-2.5 px-6 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-900/30 transition-all cursor-pointer disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
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
