import axios from 'axios';

// Khi chạy dev qua Vite proxy, /api sẽ tự động forward về http://127.0.0.1:8000
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tự động gắn Bearer Token nếu có trong localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('pytutor_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ==============================================================================
// AUTH API
// ==============================================================================

export const loginApi = async (username, password) => {
  const response = await apiClient.post('/auth/login', { username, password });
  return response.data;
};

export const getMeApi = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

// ==============================================================================
// HEALTH & EXERCISES (STUDENT)
// ==============================================================================

export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Lỗi checkHealth:', error);
    return {
      status: 'error',
      mcp_server_connected: false,
      discovered_tools: [],
    };
  }
};

export const fetchExercises = async () => {
  const response = await apiClient.get('/exercises');
  return response.data;
};

export const fetchExerciseDetail = async (exerciseId) => {
  const response = await apiClient.get(`/exercises/${exerciseId}`);
  return response.data;
};

// ==============================================================================
// CODE EXECUTION & TUTORING
// ==============================================================================

export const runTestOnly = async ({ exercise_id, code }) => {
  const response = await apiClient.post('/run-test', {
    exercise_id,
    code,
  });
  return response.data;
};

export const submitCode = async ({ exercise_id, code, hint_level = 1, session_id = 'default_session', exam_session_id = null, action_type = 'submit' }) => {
  const payload = {
    exercise_id,
    code,
    hint_level,
    session_id,
    action_type,
  };
  if (exam_session_id) {
    payload.exam_session_id = exam_session_id;
  }
  const response = await apiClient.post('/submit', payload);
  return response.data;
};

export const fetchStudentModel = async (sessionId) => {
  const response = await apiClient.get(`/student-model/${sessionId}`);
  return response.data;
};

export const fetchStudentProfile = async (sessionId, exerciseId = '', classId = null) => {
  const params = { session_id: sessionId, exercise_id: exerciseId };
  if (classId) params.class_id = classId;
  const response = await apiClient.get(`/student/profile`, { params });
  return response.data;
};

// ==============================================================================
// PHASE 8: MULTI-TURN CHAT & CUSTOM INPUT RUN
// ==============================================================================

export const sendTutorChatMessage = async ({ exercise_id, code, session_id, user_message, history, exam_session_id = null }) => {
  const payload = {
    exercise_id,
    code,
    session_id,
    user_message,
    history,
  };
  if (exam_session_id) {
    payload.exam_session_id = exam_session_id;
  }
  const response = await apiClient.post('/tutor/chat', payload);
  return response.data;
};

export const runCustomInput = async ({ exercise_id, code, custom_input }) => {
  const response = await apiClient.post('/custom-run', {
    exercise_id,
    code,
    custom_input,
  });
  return response.data;
};



// ==============================================================================
// INSTRUCTOR DASHBOARD API
// ==============================================================================

export const fetchInstructorDashboard = async () => {
  const response = await apiClient.get('/instructor/dashboard');
  return response.data;
};

export const fetchInstructorSubmissions = async () => {
  const response = await apiClient.get('/instructor/submissions');
  return response.data;
};

export const fetchSingleSubmission = async (submissionId) => {
  const response = await apiClient.get(`/instructor/submissions/${submissionId}`);
  return response.data;
};

export const fetchInstructorExercises = async () => {
  const response = await apiClient.get('/instructor/exercises');
  return response.data;
};

export const createInstructorExercise = async (exerciseData) => {
  const response = await apiClient.post('/instructor/exercises', exerciseData);
  return response.data;
};

export const updateInstructorExercise = async (exerciseId, exerciseData) => {
  const response = await apiClient.put(`/instructor/exercises/${exerciseId}`, exerciseData);
  return response.data;
};

export const deleteInstructorExercise = async (exerciseId) => {
  const response = await apiClient.delete(`/instructor/exercises/${exerciseId}`);
  return response.data;
};

// ==============================================================================
// PHASE 9: EXECUTION STEP VISUALIZER & SKILL ROADMAP
// ==============================================================================

export const fetchExecutionTrace = async ({ code, stdin_input = '', max_steps = 150 }) => {
  const response = await apiClient.post('/trace-execution', {
    code,
    stdin_input,
    max_steps,
  });
  return response.data;
};

export const fetchSkillRoadmap = async (sessionId = 'default_session', classId = null) => {
  const params = { session_id: sessionId };
  if (classId) params.class_id = classId;
  const response = await apiClient.get('/skill-roadmap', { params });
  return response.data;
};

// ==============================================================================
// PHASE 10: GAMIFICATION, STARS, BADGES & PYTHONIC REVIEW
// ==============================================================================

export const fetchLeaderboard = async (limit = 20) => {
  const response = await apiClient.get('/leaderboard', {
    params: { limit },
  });
  return response.data;
};

export const fetchUserAchievements = async (username = 'student') => {
  const response = await apiClient.get('/student/achievements', {
    params: { username },
  });
  return response.data;
};

export const requestPythonicReview = async ({ exercise_id, code, username = 'student' }) => {
  const response = await apiClient.post('/tutor/pythonic-review', {
    exercise_id,
    code,
    username,
  });
  return response.data;
};

// ==============================================================================
// PHASE 12, 13 & 14: NEU CREDIT CLASSES, LMS ENROLLMENT & CURRICULUM MATRIX
// ==============================================================================

export const fetchClasses = async (instructorUsername = null, studentUsername = null) => {
  const params = {};
  if (instructorUsername) params.instructor_username = instructorUsername;
  if (studentUsername) params.student_username = studentUsername;
  const response = await apiClient.get('/classes', { params });
  return response.data;
};

export const fetchMyClasses = async () => {
  const response = await apiClient.get('/student/my-classes');
  return response.data;
};

export const createInstructorClass = async (classData) => {
  const response = await apiClient.post('/instructor/classes', classData);
  return response.data;
};

export const enrollClass = async (classId, studentUsername = null) => {
  const payload = studentUsername ? { student_username: studentUsername } : {};
  const response = await apiClient.post(`/classes/${classId}/enroll`, payload);
  return response.data;
};

export const enrollClassByCode = async (enrollmentCode) => {
  const response = await apiClient.post('/classes/enroll-by-code', { enrollment_code: enrollmentCode });
  return response.data;
};

export const leaveClass = async (classId) => {
  const response = await apiClient.delete(`/classes/${classId}/leave`);
  return response.data;
};

export const fetchClassCurriculum = async (classId, studentUsername) => {
  const params = studentUsername ? { student_username: studentUsername } : {};
  const response = await apiClient.get(`/classes/${classId}/curriculum`, { params });
  return response.data;
};

export const assignClassExercise = async (classId, exerciseData) => {
  const response = await apiClient.post(`/instructor/classes/${classId}/exercises`, exerciseData);
  return response.data;
};

export const updateClassExercise = async (classId, exerciseId, exerciseData) => {
  const response = await apiClient.put(`/instructor/classes/${classId}/exercises/${exerciseId}`, exerciseData);
  return response.data;
};

export const removeClassExercise = async (classId, exerciseId) => {
  const response = await apiClient.delete(`/instructor/classes/${classId}/exercises/${exerciseId}`);
  return response.data;
};

export const fetchClassStudents = async (classId) => {
  const response = await apiClient.get(`/instructor/classes/${classId}/students`);
  return response.data;
};

export const fetchExamSessions = async (classId = null, sessionType = null) => {
  const params = {};
  if (classId) params.class_id = classId;
  if (sessionType) params.session_type = sessionType;
  const response = await apiClient.get('/exam-sessions', { params });
  return response.data;
};

export const createInstructorExamSession = async (sessionData) => {
  const response = await apiClient.post('/instructor/exam-sessions', sessionData);
  return response.data;
};

export const deleteInstructorExamSession = async (sessionId) => {
  const response = await apiClient.delete(`/instructor/exam-sessions/${sessionId}`);
  return response.data;
};



