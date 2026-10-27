import logging
import os
from datetime import datetime
from typing import Optional, Union

from fastapi import Request

from app.db import connect

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
LOG_FILE = os.path.join(LOG_DIR, "rxweb-ops.log")

_logger = logging.getLogger("rxweb.ops")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    _logger.addHandler(stream_handler)
    _logger.propagate = False


def client_ip(request: Optional[Request] = None) -> str:
    if request is None:
        return ""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host or ""
    return ""


def write_log(
    action: str,
    *,
    username: str = "",
    target_type: str = "",
    target_id: Optional[Union[str, int]] = "",
    detail: str = "",
    result: str = "success",
    request: Optional[Request] = None,
) -> None:
    """写入操作日志：数据库 + 文件，失败不影响主业务。"""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = client_ip(request)
    target_id = "" if target_id is None else str(target_id)
    line = (
        f"[{result}] user={username or '-'} action={action} "
        f"target={target_type}:{target_id or '-'} ip={ip or '-'} {detail}"
    ).strip()
    try:
        _logger.info(line)
    except Exception:
        pass
    try:
        conn = connect()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL,
                username TEXT,
                action TEXT NOT NULL,
                target_type TEXT,
                target_id TEXT,
                detail TEXT,
                result TEXT NOT NULL DEFAULT 'success',
                ip TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO operation_logs
            (created_at, username, action, target_type, target_id, detail, result, ip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (created_at, username or "", action, target_type or "", target_id, detail or "", result, ip),
        )
        conn.commit()
        conn.close()
    except Exception:
        _logger.exception("写入操作日志表失败")
