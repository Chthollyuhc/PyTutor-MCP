import React, { useState, useEffect } from 'react';
import { 
  X, Layers, Cpu, Terminal, CheckCircle2, Clock, ShieldCheck, Sparkles, 
  Activity, RefreshCw, Copy, Check, Scale, Globe, AlertTriangle, 
  Database, Brain, Code2, Server, ArrowUpRight, Zap
} from 'lucide-react';
import { checkHealth } from '../services/api';

// ==============================================================================
// 1. ĐỊNH NGHĨA 8 CÔNG CỤ MCP PHÂN THEO 3 KHỐI CHỨC NĂNG
// ==============================================================================
export const MCP_FUNCTIONAL_GROUPS = [
  {
    groupId: 'code_execution',
    title: 'Khối 1: Thực thi & Phân tích Code (Chống AI đoán mò)',
    badge: 'Ground Truth Engine',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    description: 'Thực thi mã nguồn thật trong hộp cát an toàn và mổ xẻ cây cú pháp trừu tượng, cung cấp dữ liệu chạy thực tế cho AI.',
    tools: [
      {
        name: 'run_test_cases',
        title: 'Hộp cát Thực thi Mã an toàn (Sandbox Execution)',
        role: 'Chạy code trong Sandbox cô lập (timeout 5.0s), chấm điểm PASS/FAIL thực tế theo từng test case chuẩn.',
        input: 'code: str, test_cases: list[dict], timeout_seconds: float = 5.0',
        output: 'dict: passed_tests, total_tests, all_passed, results[status, actual_output, stderr, execution_time_ms]',
        safety: 'Timeout 5s chống vòng lặp vô hạn, UTF-8 subprocess cô lập',
      },
      {
        name: 'analyze_code_ast',
        title: 'Phân tích Cây Cú pháp Trừu tượng Tĩnh (AST Static Analyzer)',
        role: 'Mổ xẻ cấu trúc mã Python tĩnh không cần chạy mã. Nhận diện lỗi cú pháp SyntaxError, phát hiện vòng lặp for/while, đệ quy, biến tích lũy accumulator (+=, *=, .append).',
        input: 'code: str',
        output: 'dict: valid, syntax_error, line_count, has_loops, has_recursion, has_accumulator, structural_summary',
        safety: 'Phân tích cú pháp tĩnh an toàn, không kích hoạt mã độc',
      },
      {
        name: 'trace_code_execution',
        title: 'Truy vết Từng bước Thực thi (Execution Step Tracer)',
        role: 'Ghi lại chi tiết từng bước chuyển đổi trạng thái thực thi của chương trình (dòng lệnh chạy, giá trị các biến cục bộ/toàn cục, sự kiện gọi hàm/trả về và luồng stdout).',
        input: 'code: str, stdin_input: str = "", max_steps: int = 150',
        output: 'dict: total_steps: int, steps: list[StepFrame], stdout: str, error: Optional[str]',
        safety: 'Giới hạn tối đa 150 bước, timeout 3.0s ngắt an toàn',
      }
    ]
  },
  {
    groupId: 'data_catalog',
    title: 'Khối 2: Quản lý Ngân hàng Học liệu (SQLite Data Engine)',
    badge: 'Context Provider',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    description: 'Truy xuất ngân hàng đề bài và bộ dữ liệu kiểm thử chuẩn làm Ground Truth đối chiếu chấm điểm độc lập.',
    tools: [
      {
        name: 'get_exercise_list',
        title: 'Khám phá Danh mục Bài tập (Exercise Catalog)',
        role: 'Truy vấn danh mục bài tập lập trình Python từ cơ sở dữ liệu SQLite qua giao thức MCP, cung cấp độ khó và số lượng test cases.',
        input: 'Không có tham số',
        output: 'dict: total: int, exercises: list[ExerciseSummary]',
        safety: 'Chỉ đọc (Read-only), lọc bài tập kích hoạt is_active = 1',
      },
      {
        name: 'get_exercise_details',
        title: 'Lấy Chi tiết Đề bài & Bộ Kiểm thử Chuẩn (Exercise Details)',
        role: 'Lấy đề bài Markdown, starter code và danh sách test cases chuẩn làm Ground Truth để AI không bao giờ bị ảo giác.',
        input: 'exercise_id: str',
        output: 'dict: id, title, difficulty, category, description, starter_code, test_cases',
        safety: 'Kiểm tra tồn tại và tự động fallback nếu cơ sở dữ liệu bận',
      }
    ]
  },
  {
    groupId: 'pedagogy_memory',
    title: 'Khối 3: Trí nhớ Sư phạm & Cá nhân hóa (Stateful Memory)',
    badge: 'Adaptive ITS Memory',
    badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    description: 'Lưu trữ vết học tập và tổng hợp mô hình năng lực người học theo thời gian thực, biến LLM thành gia sư thích ứng cá nhân.',
    tools: [
      {
        name: 'save_learning_event',
        title: 'Ghi nhận Sự kiện Học tập (Learning Event Logger)',
        role: 'Lưu trữ vết học tập gồm mã nguồn, cấp độ gợi ý, số test đạt và phản hồi sư phạm của AI vào bảng submissions trong SQLite.',
        input: 'session_id, exercise_id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint',
        output: 'dict: status: "saved", submission_id: int',
        safety: 'Giao dịch SQLite WAL mode chống xung đột ghi',
      },
      {
        name: 'get_attempt_history',
        title: 'Truy xuất Lịch sử Nộp bài (Adaptive Attempt History)',
        role: 'Lấy 5 lần nộp gần nhất của học viên đối với bài tập hiện tại, giúp AI nhận thức tiến trình sửa sai để không gợi ý trùng lặp.',
        input: 'session_id: str, exercise_id: str, limit: int = 5',
        output: 'dict: session_id, exercise_id, attempts: list[AttemptItem]',
        safety: 'Giới hạn limit=5 để tối ưu hóa context window của LLM',
      },
      {
        name: 'get_student_model',
        title: 'Tính toán Mô hình Học sinh Thích ứng (Student Model)',
        role: 'Tổng hợp năng lực của người học trong thời gian thực: bài tập đã làm chủ (mastered), bài tập đang gặp khó khăn (struggling) và mức độ cần hỗ trợ trung bình.',
        input: 'session_id: str',
        output: 'dict: total_exercises_attempted, total_submissions, mastered_exercises, struggling_exercises, average_hint_level, summary',
        safety: 'Tổng hợp thống kê thích ứng cục bộ, bảo mật thông tin người học',
      }
    ]
  }
];

// ==============================================================================
// 2. CẤU HÌNH CẮM ĐA NỀN TẢNG (MULTI-HOST CONFIGURATIONS)
// ==============================================================================
const CONFIG_SNIPPETS = {
  claude_desktop: {
    title: 'Claude Desktop App',
    targetFile: 'claude_desktop_config.json',
    pathHint: '%APPDATA%\\Claude\\claude_desktop_config.json (Windows)',
    jsonContent: `{
  "mcpServers": {
    "pytutor-engine": {
      "command": "py",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\\\Users\\\\Admin\\\\Downloads\\\\Sales-support-AI-pilot",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}`
  },
  cursor: {
    title: 'Cursor IDE',
    targetFile: '.cursor/mcp.json',
    pathHint: 'Thư mục gốc của dự án hoặc %USERPROFILE%\\.cursor\\mcp.json',
    jsonContent: `{
  "mcpServers": {
    "pytutor-engine": {
      "command": "py",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}`
  },
  vscode: {
    title: 'VS Code (GitHub Copilot / Cline)',
    targetFile: 'settings.json',
    pathHint: '.vscode/settings.json hoặc Cline MCP Settings',
    jsonContent: `{
  "cline.mcpServers": {
    "pytutor-engine": {
      "command": "py",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      },
      "disabled": false,
      "autoApprove": [
        "run_test_cases",
        "analyze_code_ast",
        "get_exercise_list",
        "get_exercise_details",
        "trace_code_execution"
      ]
    }
  }
}`
  }
};

export default function MCPInspectorModal({ 
  isOpen, 
  onClose, 
  discoveredTools = [], 
  mcpTrace = [] 
}) {
  const [activeTab, setActiveTab] = useState('trace'); // 'trace' | 'comparison' | 'hosts'
  const [activeHostTab, setActiveHostTab] = useState('claude_desktop');
  const [copiedKey, setCopiedKey] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [liveTools, setLiveTools] = useState(discoveredTools);
  const [refreshNotice, setRefreshNotice] = useState(null);
  const [compilerConfig, setCompilerConfig] = useState(null);

  // Đóng modal bằng phím Escape
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Đồng bộ discoveredTools và nạp compiler_config khi mở modal
  useEffect(() => {
    if (discoveredTools && discoveredTools.length > 0) {
      setLiveTools(discoveredTools);
    }
    if (isOpen) {
      checkHealth().then(data => {
        if (data?.compiler_config) {
          setCompilerConfig(data.compiler_config);
        }
        if (data?.discovered_tools) {
          setLiveTools(data.discovered_tools);
        }
      }).catch(err => console.error(err));
    }
  }, [isOpen, discoveredTools]);

  if (!isOpen) return null;

  // Thực hiện Live Discovery lại với Backend qua /api/health
  const handleLiveDiscovery = async () => {
    setIsRefreshing(true);
    setRefreshNotice(null);
    try {
      const data = await checkHealth();
      if (data && data.discovered_tools) {
        setLiveTools(data.discovered_tools);
        if (data.compiler_config) {
          setCompilerConfig(data.compiler_config);
        }
        setRefreshNotice(`✅ Khám phá thành công ${data.discovered_tools.length} công cụ & cấu hình Trình biên dịch qua MCP JSON-RPC 2.0 (stdio)!`);
      } else {
        setRefreshNotice('⚠️ Kết nối thành công nhưng chưa nhận diện được danh sách công cụ.');
      }
    } catch (err) {
      setRefreshNotice('❌ Lỗi kết nối tới MCP Host Backend.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleCopyConfig = (key, text) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const totalToolsCount = liveTools.length || 8;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/85 backdrop-blur-md select-text animate-fade-in">
      <div className="w-full max-w-5xl max-h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold shadow-sm">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                  Model Context Protocol (MCP) Showcase Center
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono font-medium">
                  JSON-RPC 2.0 stdio
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono font-medium hidden sm:inline">
                  v3.5 Defense-Ready
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Trực quan hóa giá trị cốt lõi, nhật ký gọi công cụ và khả năng tái sử dụng đa nền tảng của MCP
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
            title="Đóng (phím Esc)"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* 3 Main Navigation Tabs */}
        <div className="px-5 pt-2.5 bg-slate-950/60 border-b border-slate-800 flex items-center space-x-2 text-xs shrink-0 overflow-x-auto">
          <button
            onClick={() => setActiveTab('trace')}
            className={`pb-2.5 px-3 font-semibold border-b-2 transition-all cursor-pointer flex items-center space-x-2 whitespace-nowrap ${
              activeTab === 'trace'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="w-4 h-4" />
            <span>🔌 8 Công cụ & Nhật ký MCP</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/15 text-emerald-300 font-mono border border-emerald-500/30">
              {totalToolsCount}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('comparison')}
            className={`pb-2.5 px-3 font-semibold border-b-2 transition-all cursor-pointer flex items-center space-x-2 whitespace-nowrap ${
              activeTab === 'comparison'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Scale className="w-4 h-4" />
            <span>⚖️ Tại sao dùng MCP?</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-cyan-500/15 text-cyan-300 font-mono border border-cyan-500/30">
              Đối chiếu
            </span>
          </button>

          <button
            onClick={() => setActiveTab('hosts')}
            className={`pb-2.5 px-3 font-semibold border-b-2 transition-all cursor-pointer flex items-center space-x-2 whitespace-nowrap ${
              activeTab === 'hosts'
                ? 'border-amber-500 text-amber-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>🌐 Cắm Đa Nền Tảng (Multi-Host)</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-amber-500/15 text-amber-300 font-mono border border-amber-500/30">
              Chuẩn USB-C
            </span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">

          {/* ============================================================================== */}
          {/* TAB 1: 8 CÔNG CỤ MCP & NHẬT KÝ THỰC THI (LIVE TRACE) */}
          {/* ============================================================================== */}
          {activeTab === 'trace' && (
            <div className="space-y-4">
              
              {/* Header Bar with Live Discovery Trigger */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                <div className="flex items-center space-x-2 text-xs text-slate-300">
                  <Terminal className="w-4 h-4 text-emerald-400" />
                  <span>
                    Giao tiếp: <span className="font-mono text-emerald-400 font-semibold">JSON-RPC 2.0 qua stdio</span>
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-400">Trạng thái: Sẵn sàng ({totalToolsCount} Tools)</span>
                </div>

                <button
                  type="button"
                  onClick={handleLiveDiscovery}
                  disabled={isRefreshing}
                  className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-emerald-300 transition-colors cursor-pointer self-start sm:self-auto disabled:opacity-50"
                  title="Gửi yêu cầu tools/list qua giao thức MCP để khám phá động danh mục công cụ trực tiếp"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
                  <span>{isRefreshing ? 'Đang khám phá...' : '🔄 Khám phá lại Tools (Live Discovery)'}</span>
                </button>
              </div>

              {refreshNotice && (
                <div className="p-2.5 rounded-lg bg-slate-950 border border-emerald-500/40 text-xs text-emerald-300 font-medium animate-fade-in flex items-center space-x-2">
                  <Sparkles className="w-3.5 h-3.5 shrink-0" />
                  <span>{refreshNotice}</span>
                </div>
              )}

              {/* 1.0. Cấu hình Trình biên dịch & Hạ tầng Thực thi (Python Compiler & Sandbox Specs) */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-cyan-500/40 space-y-3 shadow-lg">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-bold shrink-0">
                      <Terminal className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs sm:text-sm font-bold text-white flex items-center space-x-2">
                        <span>⚙️ Cấu hình Trình biên dịch & Hạ tầng Thực thi (Compiler & Sandbox)</span>
                        <span className="text-[10px] px-2 py-0.2 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-mono">
                          Python 3.14 Sandbox
                        </span>
                      </h4>
                      <p className="text-[11px] text-slate-400">
                        Thông số kỹ thuật vận hành thực tế của Runtime Subprocess và Hộp cát MCP Sandbox
                      </p>
                    </div>
                  </div>
                  <span className="text-[11px] text-emerald-400 font-mono flex items-center space-x-1 shrink-0">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Cô lập tiến trình (Process Isolation)</span>
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                      Trình thông dịch (Python Interpreter Path):
                    </span>
                    <div className="font-mono text-cyan-300 text-[11px] truncate" title={compilerConfig?.executable_path}>
                      {compilerConfig?.executable_path || 'C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'}
                    </div>
                    <span className="text-[10px] text-slate-500">
                      Version: {compilerConfig?.python_version || '3.14.0'} • Nền tảng: {compilerConfig?.platform || 'win32'}
                    </span>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                      Cờ thực thi & Bảng mã (Execution Flags & I/O):
                    </span>
                    <div className="font-mono text-amber-300 text-[11px]">
                      python -u -c &lt;code&gt; (Unbuffered, in-memory)
                    </div>
                    <span className="text-[10px] text-slate-500">
                      Bảng mã: {compilerConfig?.encoding || 'utf-8 (PYTHONIOENCODING=utf-8)'}
                    </span>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                      Cơ chế cô lập & Giao tiếp (Isolation & Protocol):
                    </span>
                    <div className="text-slate-200 text-[11px]">
                      {compilerConfig?.isolation_mechanism || 'OS Subprocess Popen via MCP JSON-RPC 2.0 stdio'}
                    </div>
                    <span className="text-[10px] text-slate-500">
                      Tách biệt 100% không gian tiến trình, không làm sập Web Server khi gặp lỗi crash/loop
                    </span>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                      Giới hạn tài nguyên & Bộ nhớ (Resource Limits):
                    </span>
                    <div className="text-slate-200 text-[11px]">
                      Sandbox: <strong className="text-rose-400">{compilerConfig?.sandbox_timeout_seconds || 5.0}s timeout</strong> • Tracer: <strong className="text-emerald-400">150 bước / 3.0s</strong>
                    </div>
                    <span className="text-[10px] text-slate-500">
                      Cơ sở dữ liệu: {compilerConfig?.database_engine || 'SQLite3 WAL Mode (timeout=20.0s)'}
                    </span>
                  </div>
                </div>
              </div>

              {/* 1.1. Phân nhóm trực quan 8 MCP Tools theo 3 Khối chức năng */}
              <div>
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Danh Mục 8 Công Cụ MCP (Phân Theo 3 Khối Chức Năng Cốt Lõi)</span>
                </h3>

                <div className="space-y-3.5">
                  {MCP_FUNCTIONAL_GROUPS.map((group) => (
                    <div 
                      key={group.groupId}
                      className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/90 space-y-3"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-2 border-b border-slate-800/80">
                        <div>
                          <h4 className="text-xs sm:text-sm font-bold text-white">
                            {group.title}
                          </h4>
                          <p className="text-[11px] text-slate-400 mt-0.5">
                            {group.description}
                          </p>
                        </div>
                        <span className={`text-[10px] px-2.5 py-0.5 rounded-full border font-mono font-medium self-start sm:self-center shrink-0 ${group.badgeColor}`}>
                          {group.badge}
                        </span>
                      </div>

                      {/* Tool Items Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
                        {group.tools.map((tool) => (
                          <div 
                            key={tool.name}
                            className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors space-y-2 flex flex-col justify-between"
                          >
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-mono font-bold text-emerald-400 text-xs">
                                  {tool.name}
                                </span>
                                <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono">
                                  @mcp.tool
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 leading-snug">
                                {tool.role}
                              </p>
                            </div>

                            <div className="pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 space-y-0.5">
                              <div>
                                <span className="text-slate-400">🛡️ An toàn: </span>
                                <span className="text-cyan-400">{tool.safety}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 1.2. Nhật ký mcp_trace thời gian thực của phiên làm việc */}
              <div className="pt-2">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Activity className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Nhật Ký Gọi Giao Thức MCP Thực Tế (Execution Trace Của Lần Chạy Gần Nhất)</span>
                </h3>

                {mcpTrace && mcpTrace.length > 0 ? (
                  <div className="space-y-2">
                    {mcpTrace.map((item, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-950 border border-slate-800/90 rounded-xl p-3.5 hover:border-slate-700 transition-all text-xs space-y-2"
                      >
                        <div className="flex items-center justify-between flex-wrap gap-2">
                          <div className="flex items-center space-x-2">
                            <span className="w-5 h-5 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-mono text-[10px] text-slate-300 font-bold">
                              {item.step || idx + 1}
                            </span>
                            <span className="font-mono text-emerald-400 font-semibold">{item.tool_name}</span>
                            <span className="text-slate-500">•</span>
                            <span className="text-slate-300 font-medium">{item.action}</span>
                          </div>

                          <div className="flex items-center space-x-2 font-mono text-[11px]">
                            <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400 flex items-center space-x-1">
                              <Clock className="w-3 h-3 text-cyan-400" />
                              <span>{item.duration_ms} ms</span>
                            </span>
                            <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold">
                              {item.status}
                            </span>
                          </div>
                        </div>

                        <div className="p-2 rounded bg-slate-900/80 border border-slate-800 font-mono text-[11px] text-slate-400 flex items-center space-x-2">
                          <span className="text-slate-500">Output Summary:</span>
                          <span className="text-slate-200">{item.summary}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 rounded-xl bg-slate-950/40 border border-slate-800/60 text-center text-xs text-slate-500 space-y-1">
                    <p>Chưa có nhật ký `mcp_trace` trong phiên này.</p>
                    <p className="text-[11px] text-slate-600">
                      Hãy bấm <b>▶ Chạy thử</b> hoặc <b>🚀 Nộp bài</b> ở màn hình IDE để quan sát chuỗi JSON-RPC 2.0 thực thi trực tiếp tại đây!
                    </p>
                  </div>
                )}
              </div>

            </div>
          )}

          {/* ============================================================================== */}
          {/* TAB 2: TẠI SAO DÙNG MCP? (BẢNG ĐỐI CHIẾU KIẾN TRÚC ĐỘC QUYỀN) */}
          {/* ============================================================================== */}
          {activeTab === 'comparison' && (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-800/40 text-xs text-cyan-300 leading-relaxed">
                <span className="font-bold text-white">💡 Vũ khí cốt lõi để bảo vệ trước Hội đồng: </span>
                MCP giải quyết triệt để 5 "căn bệnh nan y" của việc ứng dụng AI truyền thống vào giáo dục lập trình (Ảo giác kết quả code, nguy cơ crash hệ thống do code sinh viên lặp vô hạn, tính hay quên của LLM API, và sự phân mảnh công nghệ).
              </div>

              {/* Architectural Comparison Matrix */}
              <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
                <table className="min-w-full text-xs text-left">
                  <thead className="bg-slate-900/90 text-slate-300 border-b border-slate-800">
                    <tr>
                      <th className="p-3.5 font-bold w-1/4">Khía cạnh cốt lõi</th>
                      <th className="p-3.5 font-bold w-3/8 text-rose-400 bg-rose-950/20">
                        ❌ AI Truyền thống (Không có MCP)
                      </th>
                      <th className="p-3.5 font-bold w-3/8 text-emerald-400 bg-emerald-950/20">
                        ✅ Kiến trúc PyTutor-MCP
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80">
                    {/* Row 1 */}
                    <tr className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3.5 align-top">
                        <div className="font-bold text-white">1. Độ chính xác Sư phạm (Ground Truth)</div>
                        <div className="text-[11px] text-slate-500 mt-0.5">Xác định kết quả chạy code</div>
                      </td>
                      <td className="p-3.5 align-top text-slate-400 bg-rose-950/10 leading-relaxed">
                        Chỉ "đọc" code bằng mắt dạng text và <span className="text-rose-400 font-semibold">đoán xác suất token</span>. Rất dễ bị ảo giác (hallucination), khẳng định sai kết quả kiểm thử hoặc không phát hiện lỗi tràn số/vòng lặp.
                      </td>
                      <td className="p-3.5 align-top text-slate-300 bg-emerald-950/10 leading-relaxed">
                        Gọi công cụ <span className="font-mono text-emerald-400 font-semibold">run_test_cases</span>, <span className="font-mono text-emerald-400 font-semibold">analyze_code_ast</span>, <span className="font-mono text-emerald-400 font-semibold">trace_code_execution</span>. AI nhận kết quả thực thi thật 100% trước khi phát biểu gợi ý sư phạm.
                      </td>
                    </tr>

                    {/* Row 2 */}
                    <tr className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3.5 align-top">
                        <div className="font-bold text-white">2. An toàn & Cô lập (Process Isolation)</div>
                        <div className="text-[11px] text-slate-500 mt-0.5">Bảo vệ máy chủ backend</div>
                      </td>
                      <td className="p-3.5 align-top text-slate-400 bg-rose-950/10 leading-relaxed">
                        Thường chạy code trực tiếp trong tiến trình Web Server bằng <code className="text-rose-400 font-mono">exec()</code> hoặc <code className="text-rose-400 font-mono">eval()</code>. Nếu sinh viên viết <code className="text-rose-400 font-mono">while True: pass</code>, toàn bộ Web Server sẽ bị <span className="text-rose-400 font-semibold">treo cứng hoặc sập dịch vụ</span>.
                      </td>
                      <td className="p-3.5 align-top text-slate-300 bg-emerald-950/10 leading-relaxed">
                        MCP Server hoạt động như một <span className="text-emerald-400 font-semibold">tiến trình độc lập cô lập</span>. Giao tiếp qua pipe <code className="text-emerald-400 font-mono">stdio</code>, tự động cưỡng chế ngắt Timeout an toàn (5.0s / 3.0s) bảo vệ Web Server vĩnh viễn.
                      </td>
                    </tr>

                    {/* Row 3 */}
                    <tr className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3.5 align-top">
                        <div className="font-bold text-white">3. Trí nhớ Dài hạn (Stateful Pedagogy)</div>
                        <div className="text-[11px] text-slate-500 mt-0.5">Cá nhân hóa người học</div>
                      </td>
                      <td className="p-3.5 align-top text-slate-400 bg-rose-950/10 leading-relaxed">
                        Stateless API: <span className="text-rose-400 font-semibold">"Quên sạch sành sanh"</span> sau mỗi câu prompt. Không biết học viên đã nộp bài này lần thứ mấy, trước đó đã gợi ý gì, dẫn đến việc lặp lại các câu hỏi mở gây ức chế cho sinh viên.
                      </td>
                      <td className="p-3.5 align-top text-slate-300 bg-emerald-950/10 leading-relaxed">
                        Cung cấp <span className="font-mono text-emerald-400 font-semibold">get_student_model</span> và <span className="font-mono text-emerald-400 font-semibold">get_attempt_history</span>. AI nhận biết học viên đang tiến bộ hay bế tắc để tự động leo thang cấp độ gợi ý phù hợp (Scaffolding).
                      </td>
                    </tr>

                    {/* Row 4 */}
                    <tr className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3.5 align-top">
                        <div className="font-bold text-white">4. Khám phá Động (Dynamic Discovery)</div>
                        <div className="text-[11px] text-slate-500 mt-0.5">Khả năng mở rộng công cụ</div>
                      </td>
                      <td className="p-3.5 align-top text-slate-400 bg-rose-950/10 leading-relaxed">
                        Hardcoded Integration: Khi muốn bổ sung một công cụ mới, lập trình viên phải sửa đổi hàng loạt file Router, Controller, DTO và prompt thủ công.
                      </td>
                      <td className="p-3.5 align-top text-slate-300 bg-emerald-950/10 leading-relaxed">
                        Chuẩn mở MCP: Chỉ cần thêm decorator <code className="text-emerald-400 font-mono">@mcp.tool()</code> trên Server, MCP Host tự động khám phá qua lệnh <code className="text-emerald-400 font-mono">tools/list</code> mà không cần sửa cấu trúc Host.
                      </td>
                    </tr>

                    {/* Row 5 */}
                    <tr className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3.5 align-top">
                        <div className="font-bold text-white">5. Tính Độc lập Mô hình (Model Agnostic)</div>
                        <div className="text-[11px] text-slate-500 mt-0.5">Không bị khóa vào nhà cung cấp</div>
                      </td>
                      <td className="p-3.5 align-top text-slate-400 bg-rose-950/10 leading-relaxed">
                        Khóa chặt vào Function Calling độc quyền của từng hãng (OpenAI Tools, Google Tools,...). Khi đổi sang mô hình mã nguồn mở (Ollama / Qwen) phải viết lại toàn bộ code gọi hàm.
                      </td>
                      <td className="p-3.5 align-top text-slate-300 bg-emerald-950/10 leading-relaxed">
                        Toàn bộ 8 công cụ tuân thủ chuẩn mở quốc tế. Dễ dàng chuyển đổi giữa Gemini, Qwen2.5, Claude hoặc bất kỳ LLM nào mà không cần sửa đổi engine kiểm thử.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ============================================================================== */}
          {/* TAB 3: KHẢ NĂNG CẮM ĐA NỀN TẢNG (CHUẨN "USB-C CHO AI") */}
          {/* ============================================================================== */}
          {activeTab === 'hosts' && (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-800/40 text-xs text-amber-300 leading-relaxed">
                <span className="font-bold text-white">🌐 Chuẩn công nghệ "Cổng USB-C cho thời đại AI": </span>
                Nhờ tuân thủ chuẩn giao thức Model Context Protocol, toàn bộ 8 công cụ của PyTutor <b>KHÔNG bị giam giữ</b> trong ứng dụng web này, mà có thể "cắm nóng" vào bất kỳ phần mềm MCP Client nào trên thế giới (Claude Desktop, Cursor IDE, VS Code Copilot) mà không cần viết lại dù chỉ 1 dòng code!
              </div>

              {/* Sub-tabs for Host Clients */}
              <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
                {Object.keys(CONFIG_SNIPPETS).map((k) => {
                  const cfg = CONFIG_SNIPPETS[k];
                  const active = activeHostTab === k;
                  return (
                    <button
                      key={k}
                      type="button"
                      onClick={() => setActiveHostTab(k)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                        active
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                          : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
                      }`}
                    >
                      {cfg.title}
                    </button>
                  );
                })}
              </div>

              {/* Config Display Card */}
              {CONFIG_SNIPPETS[activeHostTab] && (
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800">
                    <div>
                      <div className="text-xs font-bold text-white flex items-center space-x-2">
                        <span>{CONFIG_SNIPPETS[activeHostTab].title} Configuration</span>
                        <span className="font-mono text-[10.5px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                          {CONFIG_SNIPPETS[activeHostTab].targetFile}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        Đường dẫn: <span className="font-mono text-slate-400">{CONFIG_SNIPPETS[activeHostTab].pathHint}</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleCopyConfig(activeHostTab, CONFIG_SNIPPETS[activeHostTab].jsonContent)}
                      className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors cursor-pointer self-start sm:self-auto border border-slate-700 shadow-sm"
                    >
                      {copiedKey === activeHostTab ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400">Đã chép cấu hình!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-slate-400" />
                          <span>📋 Sao chép cấu hình JSON</span>
                        </>
                      )}
                    </button>
                  </div>

                  <pre className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-amber-300 overflow-x-auto leading-relaxed">
                    <code>{CONFIG_SNIPPETS[activeHostTab].jsonContent}</code>
                  </pre>

                  <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 space-y-1">
                    <p className="font-semibold text-slate-300">📖 Cách áp dụng trong 30 giây:</p>
                    <ol className="list-decimal list-inside space-y-0.5 text-slate-400">
                      <li>Sao chép đoạn JSON cấu hình ở trên.</li>
                      <li>Dán vào file cấu hình tương ứng của ứng dụng ({CONFIG_SNIPPETS[activeHostTab].targetFile}).</li>
                      <li>Khởi động lại {CONFIG_SNIPPETS[activeHostTab].title} $\rightarrow$ Toàn bộ 8 công cụ của PyTutor sẽ sẵn sàng cho mô hình sử dụng ngay lập tức!</li>
                    </ol>
                  </div>
                </div>
              )}

            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="px-5 py-3 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-500 shrink-0">
          <div className="flex items-center space-x-2">
            <span>Model Context Protocol (Open Standard by Anthropic)</span>
            <span className="text-slate-600">•</span>
            <span className="text-emerald-400 font-mono font-medium">8 Tools Active</span>
          </div>
          <button
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
