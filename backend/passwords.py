"""Băm và kiểm tra mật khẩu (chỉ dùng thư viện chuẩn, không phụ thuộc module khác của backend).

Định dạng lưu: ``pbkdf2_sha256$<số vòng>$<muối hex>$<băm hex>``.

Tương thích ngược: giá trị lưu KHÔNG bắt đầu bằng tiền tố trên được coi là mật khẩu văn bản thường của cơ sở dữ liệu
cũ và vẫn được chấp nhận (so sánh thời gian hằng). Không có bước tự động ghi đè mật khẩu cũ: dữ liệu hiện có không bị
đổi khi đăng nhập; muốn chuyển sang dạng băm thì cập nhật cột `users.password` bằng `hash_password(...)`.
"""
from __future__ import annotations

import hashlib
import hmac
import os

_PREFIX = "pbkdf2_sha256"
_ITERATIONS = 200_000


def hash_password(password: str, *, iterations: int = _ITERATIONS) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{_PREFIX}${iterations}${salt.hex()}${digest.hex()}"


def is_hashed(stored: str) -> bool:
    return isinstance(stored, str) and stored.startswith(_PREFIX + "$")


def verify_password(password: str, stored: str) -> bool:
    """Đúng khi `password` khớp giá trị lưu; chấp nhận cả dạng băm và dạng văn bản thường (cơ sở dữ liệu cũ)."""
    if not isinstance(stored, str) or not isinstance(password, str):
        return False
    if is_hashed(stored):
        try:
            _, iterations, salt_hex, digest_hex = stored.split("$")
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations))
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(actual, expected)
    return hmac.compare_digest(password.encode("utf-8"), stored.encode("utf-8"))
