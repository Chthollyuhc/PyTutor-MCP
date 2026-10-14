import axios from 'axios';

// Khi chạy dev qua Vite proxy, /api sẽ tự động forward về http://127.0.0.1:8000
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
  try {
    const response = await apiClient.get('/exercises');
    return response.data;
  } catch (error) {
    console.error('Lỗi fetchExercises:', error);
    throw error;
  }
};

export const fetchExerciseDetail = async (exerciseId) => {
  try {
    const response = await apiClient.get(`/exercises/${exerciseId}`);
    return response.data;
  } catch (error) {
    console.error(`Lỗi fetchExerciseDetail(${exerciseId}):`, error);
    throw error;
  }
};

export const submitCode = async ({ exercise_id, code, hint_level = 1 }) => {
  try {
    const response = await apiClient.post('/submit', {
      exercise_id,
      code,
      hint_level,
    });
    return response.data;
  } catch (error) {
    console.error('Lỗi submitCode:', error);
    throw error;
  }
};
