import hashlib
import importlib.util
import os
import re
import secrets
import sqlite3
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from app.auth import hash_password
except Exception:
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 210000)
        return f"{salt}${digest.hex()}"


def _load_seed_module():
    """只加载当前站点的种子文件，不扫描其他公司目录。"""
    site = (os.environ.get("RXWEB_SITE") or os.environ.get("SITE_ID") or "").strip()
    explicit = (os.environ.get("RXWEB_SEED_FILE") or "").strip()
    root = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
    if site and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", site):
        raise SystemExit(f"站点名不合法：{site}")

    if explicit:
        path = os.path.abspath(explicit)
    elif site:
        source = os.path.join(root, "deploy", "sites", site, "seed_data.py")
        bundled = os.path.join(BACKEND_DIR, "site_seed.py")
        path = source if os.path.isfile(source) else bundled
    else:
        path = os.path.join(BACKEND_DIR, "site_seed.py")

    if not os.path.isfile(path):
        raise SystemExit("找不到当前站点的种子数据。请设置 SITE_ID，或在发布包中提供 backend/site_seed.py")

    spec = importlib.util.spec_from_file_location("site_seed_data", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"无法加载种子文件：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    file_site = str(getattr(module, "SITE_ID", "") or "").strip()
    if not file_site:
        raise SystemExit(f"种子文件缺少 SITE_ID：{path}")
    if site and file_site != site:
        raise SystemExit(f"种子文件属于 {file_site}，与当前站点 {site} 不一致")
    for name in ("products", "news", "messages", "downloads", "admin_email", "user_email"):
        if not hasattr(module, name):
            raise SystemExit(f"种子文件缺少 {name}：{path}")
    return module, path


_module, _seed_path = _load_seed_module()
_site = _module.SITE_ID
products = _module.products
news = _module.news
messages = _module.messages
downloads = _module.downloads
admin_email = os.environ.get("RXWEB_ADMIN_EMAIL") or _module.admin_email
user_email = os.environ.get("RXWEB_USER_EMAIL") or _module.user_email
admin_name = getattr(_module, "admin_name", "管理员")
user_name = getattr(_module, "user_name", "演示用户")

# 默认写到项目根目录 company.db；Docker 可设置 RXWEB_DB 指向数据卷
_db_path = os.environ.get(
    "RXWEB_DB",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "company.db")),
)
conn = sqlite3.connect(_db_path)
c = conn.cursor()

# 创建表
c.execute('''DROP TABLE IF EXISTS products''')
c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price TEXT,
    category TEXT,
    image TEXT,
    description TEXT
)''')
c.execute('''DROP TABLE IF EXISTS news''')
c.execute('''CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY,
    title TEXT,
    date TEXT,
    source TEXT,
    summary TEXT,
    content TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    version TEXT,
    size TEXT,
    date TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    reply TEXT,
    replied_at TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    reset_token TEXT,
    reset_expires TEXT,
    created_at TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    username TEXT,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    detail TEXT,
    result TEXT NOT NULL DEFAULT 'success',
    ip TEXT
)''')

# 清空表
c.execute('DELETE FROM products')
c.execute('DELETE FROM news')
c.execute('DELETE FROM downloads')
c.execute('DELETE FROM messages')
c.execute('DELETE FROM admins')
c.execute('DELETE FROM users')

# 插入数据
c.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)', products)
c.executemany('INSERT INTO news VALUES (?, ?, ?, ?, ?, ?)', news)
c.executemany('INSERT INTO downloads VALUES (?, ?, ?, ?, ?, ?)', downloads)
c.executemany(
    'INSERT INTO messages (name, email, subject, content, created_at, status, reply, replied_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    messages,
)
c.execute(
    'INSERT INTO admins (username, password_hash) VALUES (?, ?)',
    (os.environ.get("RXWEB_ADMIN_USER", "admin"), hash_password(os.environ.get("RXWEB_ADMIN_PASS", "rxweb123"))),
)
now = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
c.execute(
    'INSERT INTO users (email, password_hash, name, role, created_at) VALUES (?, ?, ?, ?, ?)',
    (admin_email, hash_password(os.environ.get("RXWEB_ADMIN_PASS", "rxweb123")), admin_name, "admin", now),
)
c.execute(
    'INSERT INTO users (email, password_hash, name, role, created_at) VALUES (?, ?, ?, ?, ?)',
    (user_email, hash_password(os.environ.get("RXWEB_USER_PASS", "user123")), user_name, "user", now),
)

conn.commit()
conn.close()
print(f'种子数据已写入数据库（站点：{_site}）。')
