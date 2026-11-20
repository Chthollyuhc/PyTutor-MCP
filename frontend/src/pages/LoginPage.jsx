import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight, BookOpen, CheckCircle2, Code2, Cpu, GraduationCap,
  LockKeyhole, School, ShieldCheck, Sparkles, UserRound,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Badge, Button, Card, Input } from '../components/ui';
import ThemeToggle from '../components/ThemeToggle';

const demoAccounts = [
  {
    name: 'Sinh viên NEU: Trần Minh Khánh',
    details: 'MSV: 11236131 • K65 CNTT (student / student123)',
    destination: '/student',
    username: 'student',
    password: 'student123',
    role: 'Sinh viên',
    variant: 'success',
    Icon: GraduationCap,
  },
  {
    name: 'Giảng viên 1: Nguyễn Văn A',
    details: 'Khoa CNTT - NEU (gv_tran / gv123)',
    destination: '/instructor',
    username: 'gv_tran',
    password: 'gv123',
    role: 'Giảng viên',
    variant: 'warning',
    Icon: ShieldCheck,
  },
  {
    name: 'Giảng viên 2: Trần Văn B',
    details: 'Khoa CNTT - NEU (gv_tuan / gv123)',
    destination: '/instructor',
    username: 'gv_tuan',
    password: 'gv123',
    role: 'Giảng viên',
    variant: 'info',
    Icon: ShieldCheck,
  },
];

const pillars = [
  {
    title: 'Lớp học phần NEU',
    description: 'Lộ trình học, bài tập và tiến độ được tổ chức theo từng lớp.',
    detail: 'CNTT1128 · CNTT1187',
    Icon: School,
    color: 'text-sky-700 bg-sky-50 border border-sky-200 dark:text-sky-300 dark:bg-sky-400/10 dark:border-sky-500/20',
  },
  {
    title: 'Gia sư AI Socratic',
    description: 'Gợi ý theo từng mức, khuyến khích tự tìm lời giải thay vì chép đáp án.',
    detail: '3 mức hỗ trợ',
    Icon: Sparkles,
    color: 'text-emerald-700 bg-emerald-50 border border-emerald-200 dark:text-emerald-300 dark:bg-emerald-400/10 dark:border-emerald-500/20',
  },
  {
    title: 'Chạy và phân tích mã',
    description: 'Chạy thử, phân tích cấu trúc và truy vết chương trình trong môi trường cô lập.',
    detail: 'Môi trường cô lập',
    Icon: Cpu,
    color: 'text-violet-700 bg-violet-50 border border-violet-200 dark:text-violet-300 dark:bg-violet-400/10 dark:border-violet-500/20',
  },
];

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const validateLogin = (field, value) => {
    if (value.trim()) return '';
    return field === 'username'
      ? 'Nhập tên đăng nhập (mã sinh viên hoặc tài khoản giảng viên), ví dụ student.'
      : 'Nhập mật khẩu của tài khoản. Nếu quên, liên hệ giảng viên phụ trách để được cấp lại.';
  };
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (userName, userPassword) => {
    setError('');
    setIsLoading(true);
    try {
      const userData = await login(userName, userPassword);
      navigate(userData.role === 'instructor' ? '/instructor' : '/student');
    } catch (err) {
      console.error('Lỗi đăng nhập:', err);
      setError(err.response?.data?.detail || 'Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmitForm = (event) => {
    event.preventDefault();
    const nextErrors = { username: validateLogin('username', username), password: validateLogin('password', password) };
    setFieldErrors(nextErrors);
    if (nextErrors.username || nextErrors.password) return;
    handleLogin(username.trim(), password.trim());
  };

  return (
    <main className="min-h-screen bg-canvas text-foreground selection:bg-primary/30">
      <div className="mx-auto grid min-h-screen w-full max-w-[1600px] lg:grid-cols-12">
        <aside className="relative hidden overflow-hidden border-r border-border bg-surface-raised dark:bg-slate-950 px-10 py-10 lg:col-span-7 lg:flex lg:flex-col lg:justify-between xl:px-16 xl:py-12">

          <div className="relative z-10">
            <div className="mb-16 flex items-center gap-3">
              <span className="flex size-11 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-soft">
                <Code2 aria-hidden="true" className="size-5" />
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-base font-bold tracking-tight text-foreground">PyTutor</span>
                </div>
                <p className="mt-0.5 text-xs text-muted">LMS · IDE · Gia sư thông minh</p>
              </div>
            </div>

            <Badge variant="neutral" className="mb-6">
              <School aria-hidden="true" className="size-3.5 text-emerald-600 dark:text-emerald-400" />
              Khoa CNTT · Đại học Kinh tế Quốc dân
            </Badge>
            <h1 className="max-w-2xl text-4xl font-semibold leading-tight tracking-[-0.025em] text-foreground xl:text-5xl">
              Học Python bằng cách tự làm.
            </h1>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-muted">
              Thực hành trong IDE, nhận gợi ý theo tiến độ và hiểu chương trình từ kết quả chạy thực tế.
            </p>

            <ul className="mt-12 max-w-2xl divide-y divide-border border-y border-border">
              {pillars.map(({ title, description, detail, Icon, color }) => (
                <li key={title} className="flex items-start gap-4 py-5">
                  <span className={`mt-0.5 flex size-10 shrink-0 items-center justify-center rounded-xl shadow-soft ${color}`}>
                    <Icon aria-hidden="true" className="size-5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                      <h2 className="text-sm font-semibold text-foreground">{title}</h2>
                      <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">{detail}</span>
                    </div>
                    <p className="mt-1.5 max-w-xl text-sm leading-relaxed text-muted">{description}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="relative z-10 mt-12 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-5 text-xs text-muted">
            <span>Khoa Công nghệ thông tin · NEU</span>
            <span className="inline-flex items-center gap-2 font-medium">
              <CheckCircle2 aria-hidden="true" className="size-4 text-emerald-600 dark:text-emerald-400" />
              Multi-Stage LMS &amp; IDE
            </span>
          </div>
        </aside>

        <section className="flex min-h-screen min-w-0 items-center justify-center px-4 py-8 sm:px-8 lg:col-span-5 lg:px-10 xl:px-14">
          <Card className="w-full min-w-0 max-w-lg p-6 sm:p-8 rounded-3xl shadow-bento">
            <div className="mb-4 flex justify-end">
              <ThemeToggle />
            </div>
            <div className="mb-8 lg:hidden">
              <div className="mb-5 flex items-center gap-3">
                <span className="flex size-10 items-center justify-center rounded-full bg-emerald-500 text-white shadow-soft">
                  <Code2 aria-hidden="true" className="size-5" />
                </span>
                <div>
                  <p className="font-bold tracking-tight text-foreground">PyTutor</p>
                  <p className="text-xs text-muted">Khoa CNTT · NEU</p>
                </div>
              </div>
            </div>

            <header className="mb-7">
              <h2 className="text-2xl font-bold tracking-tight text-foreground">Đăng nhập</h2>
              <p className="mt-2 text-sm leading-relaxed text-muted">
                Truy cập không gian học tập dành cho sinh viên và giảng viên NEU.
              </p>
            </header>

            {error && (
              <div role="alert" className="mb-6 rounded-md border border-destructive/35 bg-destructive/10 px-4 py-3 text-sm leading-relaxed text-danger">
                {error}
              </div>
            )}

            <form onSubmit={onSubmitForm} noValidate className="space-y-5">
              <Input
                label="Tên đăng nhập / Mã định danh"
                icon={UserRound}
                type="text"
                name="username"
                autoComplete="username"
                placeholder="student hoặc gv_tran"
                required
                disabled={isLoading}
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                onBlur={() => username && setFieldErrors((prev) => ({ ...prev, username: validateLogin('username', username) }))}
                onFocus={() => setFieldErrors((prev) => ({ ...prev, username: '' }))}
                error={fieldErrors.username}
              />
              <Input
                label="Mật khẩu"
                icon={LockKeyhole}
                type="password"
                name="password"
                autoComplete="current-password"
                placeholder="Nhập mật khẩu"
                required
                disabled={isLoading}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                onBlur={() => password && setFieldErrors((prev) => ({ ...prev, password: validateLogin('password', password) }))}
                onFocus={() => setFieldErrors((prev) => ({ ...prev, password: '' }))}
                error={fieldErrors.password}
              />
              <Button type="submit" loading={isLoading} variant="primary" className="mt-2 w-full py-3">
                {isLoading ? 'Đang xác thực tài khoản…' : 'Đăng nhập Cổng NEU'}
                {!isLoading && <ArrowRight aria-hidden="true" className="size-4" />}
              </Button>
            </form>

            <div className="mt-8 border-t border-border pt-6">
              <div className="mb-4 flex items-center justify-between gap-3">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <Sparkles aria-hidden="true" className="size-4 text-amber-500" />
                  Demo dành cho hội đồng
                </h3>
                <span className="text-xs text-muted">Chọn tài khoản để vào nhanh</span>
              </div>

              <div className="space-y-2.5">
                {demoAccounts.map(({ name, details, destination, username: demoUser, password: demoPassword, role, variant, Icon }) => (
                  <Button
                    key={demoUser}
                    type="button"
                    variant={variant}
                    disabled={isLoading}
                    onClick={() => handleLogin(demoUser, demoPassword)}
                    className="h-auto min-h-[4.5rem] w-full justify-between rounded-2xl px-4 py-3 text-left shadow-soft transition-all active:scale-[0.98] cursor-pointer"
                    aria-label={`Đăng nhập demo với vai trò ${role}: ${name}`}
                  >
                    <span className="flex min-w-0 items-center gap-3">
                      <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-black/15">
                        <Icon aria-hidden="true" className="size-4" />
                      </span>
                      <span className="min-w-0">
                        <span className="block truncate text-sm font-semibold text-slate-900 dark:text-slate-100">{name}</span>
                        <span className="mt-1 block truncate text-xs font-medium text-slate-600 dark:text-slate-300">{details}</span>
                      </span>
                    </span>
                    <span className="ml-2 hidden shrink-0 items-center gap-1 text-xs font-medium sm:inline-flex">
                      {destination === '/student' ? <BookOpen aria-hidden="true" className="size-3.5" /> : <ShieldCheck aria-hidden="true" className="size-3.5" />}
                      {role}
                    </span>
                  </Button>
                ))}
              </div>
            </div>
          </Card>
        </section>
      </div>
    </main>
  );
}
