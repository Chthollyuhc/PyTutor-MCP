"""
Module Xác thực và Phân quyền (Authentication & Authorization) cho PyTutor.
Hỗ trợ 2 vai trò:
- 'student': Sinh viên học lập trình, chạy code, nhận gợi ý AI
- 'instructor': Giảng viên quản lý ngân hàng bài tập (CRUD) và xem thống kê
"""
import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.database import get_db_connection

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "pytutor-scaffolding-jwt-secret-2026")
ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)


def create_token(username: str, role: str, full_name: str) -> str:
    """Tạo JWT Token có thời hạn 24 giờ."""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": username,
        "role": role,
        "name": full_name,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Xác minh Bearer token từ Header."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu đăng nhập để truy cập tài nguyên này."
        )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã xác thực không hợp lệ."
        )


def require_instructor(token: dict = Depends(verify_token)) -> dict:
    """Ràng buộc quyền: Chỉ Giảng viên mới được phép thực hiện."""
    if token.get("role") != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ tài khoản Giảng viên mới có quyền thực hiện thao tác này."
        )
    return token


def authenticate_user(username: str, password: str) -> dict | None:
    """Kiểm tra thông tin đăng nhập trong cơ sở dữ liệu SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, full_name, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user["password"] == password:
        return {
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"]
        }
    return None
