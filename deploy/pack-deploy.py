"""Build a production zip for one site: backend + that site's seed + frontend/dist."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

DEPLOY_DIR = Path(__file__).resolve().parent
ROOT = DEPLOY_DIR.parent
OUT_ZIP = DEPLOY_DIR / "RxWeb-deploy.zip"
FRONTEND = ROOT / "frontend"
DIST = FRONTEND / "dist"


def add_file(zf: zipfile.ZipFile, src: Path, arc: str) -> None:
    zf.write(src, arc.replace("\\", "/"))


def add_tree(zf: zipfile.ZipFile, src_dir: Path, arc_prefix: str) -> None:
    for path in src_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(src_dir).as_posix()
        if rel == "site_seed.py" or rel.startswith("seed_data/"):
            continue
        if "/__pycache__/" in f"/{rel}" or rel.endswith(".pyc"):
            continue
        add_file(zf, path, f"{arc_prefix}/{rel}")


def read_app_port(site_dir: Path, target: str) -> str:
    key = "PROD_APP_PORT" if target == "prod" else "DEBUG_APP_PORT"
    env_file = site_dir / "site.env"
    if not env_file.is_file():
        raise SystemExit(f"[error] 找不到 {env_file}")
    match = re.search(rf"(?m)^{key}=(\d+)\s*$", env_file.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"[error] {env_file} 没有可用的 {key}")
    return match.group(1)


def render_start_sh(port: str) -> str:
    text = (ROOT / "start.sh").read_text(encoding="utf-8")
    if "@RXWEB_APP_PORT@" not in text:
        raise SystemExit("[error] start.sh 缺少端口占位符 @RXWEB_APP_PORT@")
    return text.replace("@RXWEB_APP_PORT@", port).replace("\r\n", "\n").replace("\r", "\n")


def build_frontend(site: str) -> None:
    npm = shutil.which("npm")
    if not npm:
        raise SystemExit("[error] npm not found. Install Node.js, then pack again.")
    print(f"[info] building frontend/dist for site {site} ...")
    env = os.environ.copy()
    env["VITE_SITE_ID"] = site
    if not (FRONTEND / "node_modules").is_dir():
        subprocess.run([npm, "install"], cwd=FRONTEND, check=True, env=env)
    subprocess.run([npm, "run", "build"], cwd=FRONTEND, check=True, env=env)
    if not (DIST / "index.html").is_file():
        raise SystemExit("[error] frontend/dist/index.html missing after build")


def main() -> int:
    parser = argparse.ArgumentParser(description="打包一家公司的发布文件")
    parser.add_argument("--site", required=True, help="站点目录名，例如 aierde")
    parser.add_argument("--target", choices=("debug", "prod"), default="debug")
    args = parser.parse_args()
    site = args.site.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", site):
        raise SystemExit("[error] 站点名只能使用字母、数字、下划线和连字符")

    site_dir = DEPLOY_DIR / "sites" / site
    seed = site_dir / "seed_data.py"
    if not seed.is_file():
        raise SystemExit(f"[error] 找不到该站点的种子数据 {seed}")
    seed_text = seed.read_text(encoding="utf-8")
    if not re.search(rf"SITE_ID\s*=\s*['\"]{re.escape(site)}['\"]", seed_text):
        raise SystemExit(f"[error] 种子文件的 SITE_ID 不是 {site}")

    app_port = read_app_port(site_dir, args.target)
    start_text = render_start_sh(app_port)
    build_frontend(site)

    required = [
        ROOT / "backend" / "requirements.txt",
        ROOT / "backend" / "seed.py",
        ROOT / "backend" / "app" / "main.py",
    ]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        print("[error] missing files:")
        for item in missing:
            print(f"  {item}")
        return 1

    if OUT_ZIP.exists():
        OUT_ZIP.unlink()

    optional = [
        ROOT / "backend" / "app" / "__init__.py",
    ]

    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("start.sh", start_text)
        for path in required:
            add_file(zf, path, path.relative_to(ROOT).as_posix())
        for path in optional:
            if path.is_file():
                add_file(zf, path, path.relative_to(ROOT).as_posix())
        add_file(zf, seed, "backend/site_seed.py")
        add_tree(zf, ROOT / "backend" / "app", "backend/app")
        add_tree(zf, DIST, "frontend/dist")

    print(f"[done] {OUT_ZIP}")
    print(f"packed site: {site}  port: {app_port}  target: {args.target}")
    print("packed: start.sh, backend, backend/site_seed.py, frontend/dist")
    print("not packed: other sites, frontend/src, node_modules, venv, company.db")
    return 0


if __name__ == "__main__":
    sys.exit(main())
