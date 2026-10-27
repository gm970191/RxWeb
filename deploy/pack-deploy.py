#!/usr/bin/env python3
"""Build a production zip: backend + frontend/dist only. No Vue source, no company.db."""
from __future__ import annotations

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
        if path.is_file():
            rel = path.relative_to(src_dir).as_posix()
            add_file(zf, path, f"{arc_prefix}/{rel}")


def build_frontend() -> None:
    npm = shutil.which("npm")
    if not npm:
        raise SystemExit("[error] npm not found. Install Node.js, then pack again.")
    print("[info] building frontend/dist ...")
    if not (FRONTEND / "node_modules").is_dir():
        subprocess.run([npm, "install"], cwd=FRONTEND, check=True)
    subprocess.run([npm, "run", "build"], cwd=FRONTEND, check=True)
    if not (DIST / "index.html").is_file():
        raise SystemExit("[error] frontend/dist/index.html missing after build")


def main() -> int:
    build_frontend()

    required = [
        ROOT / "start.sh",
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
        for path in required:
            add_file(zf, path, path.relative_to(ROOT).as_posix())
        for path in optional:
            if path.is_file():
                add_file(zf, path, path.relative_to(ROOT).as_posix())
        add_tree(zf, DIST, "frontend/dist")

    print(f"[done] {OUT_ZIP}")
    print("packed: start.sh, backend, frontend/dist")
    print("not packed: frontend/src, node_modules, venv, company.db")
    print("unzip into the site directory from deploy/sites/<site>/site.env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
