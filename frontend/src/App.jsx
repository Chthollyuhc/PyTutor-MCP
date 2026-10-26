import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import StudentPortalPage from './pages/StudentPortalPage';
import StudentClassDetailPage from './pages/StudentClassDetailPage';
import StudentIDE from './pages/StudentIDE';
import InstructorDashboard from './pages/InstructorDashboard';
import ExerciseFormPage from './pages/ExerciseFormPage';

// Component điều hướng thông minh tại Route gốc '/'
function IndexRedirect() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen w-screen flex items-center justify-center bg-slate-950 text-slate-400 font-sans text-xs">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span>Đang tải Cổng Đào Tạo NEU PyTutor-MCP...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === 'instructor') {
    return <Navigate to="/instructor" replace />;
  }

  return <Navigate to="/student" replace />;
}

// Bọc bảo vệ route cho Sinh viên
function StudentRoute({ children }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

// Bọc bảo vệ route cho Giảng viên
function InstructorRoute({ children }) {
  const { user, isInstructor, isLoading } = useAuth();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!isInstructor) return <Navigate to="/student" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Điều hướng thông minh từ trang chủ */}
          <Route path="/" element={<IndexRedirect />} />

          {/* Màn hình đăng nhập Cổng NEU */}
          <Route path="/login" element={<LoginPage />} />

          {/* TẦNG 1 SINH VIÊN: Cổng Học tập & Danh sách Lớp Học Phần NEU */}
          <Route
            path="/student"
            element={
              <StudentRoute>
                <StudentPortalPage />
              </StudentRoute>
            }
          />

          {/* TẦNG 2 SINH VIÊN: Không gian Chi tiết Lớp Học Phần (Curriculum, Exams, Skill Roadmap, Leaderboard) */}
          <Route
            path="/student/classes/:classId"
            element={
              <StudentRoute>
                <StudentClassDetailPage />
              </StudentRoute>
            }
          />

          {/* TẦNG 3 SINH VIÊN: Môi trường Lập trình IDE Chuyên sâu 3 Cột */}
          <Route
            path="/student/ide/:exerciseId"
            element={
              <StudentRoute>
                <StudentIDE />
              </StudentRoute>
            }
          />
          <Route
            path="/student/ide"
            element={
              <StudentRoute>
                <StudentIDE />
              </StudentRoute>
            }
          />

          {/* CỔNG QUẢN TRỊ GIẢNG VIÊN NEU (Sidebar Layout Hiện Đại) */}
          <Route
            path="/instructor"
            element={
              <InstructorRoute>
                <InstructorDashboard />
              </InstructorRoute>
            }
          />
          <Route
            path="/instructor/classes/:classId"
            element={
              <InstructorRoute>
                <InstructorDashboard />
              </InstructorRoute>
            }
          />
          <Route
            path="/instructor/exercises/new"
            element={
              <InstructorRoute>
                <ExerciseFormPage />
              </InstructorRoute>
            }
          />
          <Route
            path="/instructor/exercises/:id/edit"
            element={
              <InstructorRoute>
                <ExerciseFormPage />
              </InstructorRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
