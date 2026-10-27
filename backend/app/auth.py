import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Header, HTTPException
from jose import JWTError, jwt

from app.db import connect

SECRET_KEY = os.environ.get("RXWEB_SECRET", "rxweb-dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 210000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 210000)
    return hmac.compare_digest(check.hex(), digest)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_token(email: str, role: str, name: str = "") -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": email, "role": role, "name": name, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def find_user_by_email(email: str):
    conn = connect()
    row = conn.execute(
        "SELECT id, email, password_hash, name, role, reset_token, reset_expires FROM users WHERE lower(email) = lower(?)",
        (email.strip(),),
    ).fetchone()
    conn.close()
    return row


def user_payload(row) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"] or "",
        "role": row["role"] or "user",
    }


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization[7:].strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="登录已失效")
    except JWTError:
        raise HTTPException(status_code=401, detail="登录已失效")
    row = find_user_by_email(email)
    if not row:
        raise HTTPException(status_code=401, detail="登录已失效")
    return user_payload(row)


def require_user(authorization: Optional[str] = Header(None)) -> dict:
    return get_current_user(authorization)


def require_admin(authorization: Optional[str] = Header(None)) -> dict:
    user = get_current_user(authorization)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
