"""产品图存放在项目根目录 media/，不放进 frontend/dist。

发布脚本只覆盖 frontend/dist，不会删除这个目录，所以上传的图片在下次发布后还在。
随站点构建带上的图片在 frontend/dist/media，这里只作读取兜底。
"""

import os
import re
import secrets

MEDIA_DIR = os.path.abspath(os.environ.get(
    "RXWEB_MEDIA_DIR",
    os.path.join(os.path.dirname(__file__), "../../media"),
))
DIST_MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist/media"))

MAX_IMAGE_BYTES = 2 * 1024 * 1024
_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
_SERVE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _inside(root: str, path: str) -> bool:
    root_abs = os.path.normcase(os.path.abspath(root))
    path_abs = os.path.normcase(os.path.abspath(path))
    try:
        return os.path.commonpath([root_abs, path_abs]) == root_abs
    except ValueError:
        return False


def products_dir() -> str:
    folder = os.path.join(MEDIA_DIR, "products")
    os.makedirs(folder, exist_ok=True)
    return folder


def sniff_image(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ""


def save_product_image(data: bytes) -> str:
    if not data:
        raise ValueError("文件是空的")
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("图片不能超过 2MB")
    ext = sniff_image(data)
    if not ext:
        raise ValueError("只接受 jpg、png、webp")
    folder = products_dir()
    for _ in range(5):
        name = secrets.token_hex(8) + ext
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            with open(path, "wb") as handle:
                handle.write(data)
            return name
    raise ValueError("保存图片失败，请重试")


def _media_roots() -> list:
    roots = [MEDIA_DIR]
    site = (os.environ.get("SITE_ID") or "").strip()
    if site and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", site):
        site_media = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "../../deploy/sites", site, "media",
        ))
        roots.append(site_media)
    roots.append(DIST_MEDIA_DIR)
    return roots


def list_product_image_names() -> list:
    names = set()
    for root in _media_roots():
        folder = os.path.join(root, "products")
        if not os.path.isdir(folder):
            continue
        for entry in os.listdir(folder):
            if _SEGMENT.match(entry) and os.path.splitext(entry)[1].lower() in _SERVE_EXT:
                full = os.path.join(folder, entry)
                if os.path.isfile(full):
                    names.add(entry)
    return sorted(names)


def uploaded_product_path(name: str) -> str:
    if not _SEGMENT.match(name or ""):
        return ""
    path = os.path.abspath(os.path.join(MEDIA_DIR, "products", name))
    folder = os.path.abspath(os.path.join(MEDIA_DIR, "products"))
    if not _inside(folder, path):
        return ""
    return path


def delete_uploaded_product_image(name: str) -> None:
    path = uploaded_product_path(name)
    if not path or not os.path.isfile(path):
        raise ValueError("这是随站点发布的图片，请到该站 media/products 目录里删除")
    os.remove(path)


def resolve_media_file(rel: str) -> str:
    rel = (rel or "").replace("\\", "/").lstrip("/")
    parts = [part for part in rel.split("/") if part]
    if not parts or any(not _SEGMENT.match(part) for part in parts):
        return ""
    if os.path.splitext(parts[-1])[1].lower() not in _SERVE_EXT:
        return ""
    for root in _media_roots():
        candidate = os.path.abspath(os.path.join(root, *parts))
        if _inside(root, candidate) and os.path.isfile(candidate):
            return candidate
    return ""


def clean_image_url(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if text.startswith("/media/"):
        rel = text[len("/media/"):].lstrip("/")
        if not _safe_media_url(rel):
            raise ValueError("图片路径不合法")
        return "/media/" + rel
    if text.startswith("https://") or text.startswith("http://"):
        if len(text) > 500:
            raise ValueError("图片地址过长")
        return text
    raise ValueError("图片请填站内路径或 http(s) 地址")


def _safe_media_url(rel: str) -> bool:
    """允许先填写尚未放到发布包里、但路径格式正确的站内地址。"""
    rel = rel.replace("\\", "/").lstrip("/")
    parts = [part for part in rel.split("/") if part]
    if not parts or any(not _SEGMENT.match(part) for part in parts):
        return False
    return os.path.splitext(parts[-1])[1].lower() in _SERVE_EXT
