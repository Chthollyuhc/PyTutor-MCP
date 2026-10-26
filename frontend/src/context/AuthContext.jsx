import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginApi, getMeApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('pytutor_token') || null);
  const [isLoading, setIsLoading] = useState(true);

  // Khôi phục phiên đăng nhập khi load trang
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('pytutor_token');
      const savedUser = localStorage.getItem('pytutor_user');

      if (savedToken && savedUser) {
        try {
          setUser(JSON.parse(savedUser));
          setToken(savedToken);
          // Kiểm tra tính hợp lệ của token
          const verifiedUser = await getMeApi();
          setUser(verifiedUser);
          localStorage.setItem('pytutor_user', JSON.stringify(verifiedUser));
        } catch (err) {
          console.warn('Phiên đăng nhập đã hết hạn hoặc không hợp lệ.');
          logout();
        }
      } else {
        setUser(null);
        setToken(null);
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    const data = await loginApi(username, password);
    setToken(data.access_token);
    const userData = {
      username: data.username,
      role: data.role,
      full_name: data.full_name,
    };
    setUser(userData);
    localStorage.setItem('pytutor_token', data.access_token);
    localStorage.setItem('pytutor_user', JSON.stringify(userData));
    return userData;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('pytutor_token');
    localStorage.removeItem('pytutor_user');
  };

  const isInstructor = user?.role === 'instructor';
  const isStudent = user?.role === 'student';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isLoading,
        isInstructor,
        isStudent,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
