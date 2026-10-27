# -*- coding: utf-8 -*-
"""Windows PowerShell 5.1 仍需要 UTF-8 BOM；PowerShell 7 的 deploy.ps1 不需要。"""
from pathlib import Path

root = Path(r"d:\Projects\RxWeb")
# start.ps1 等可能仍被 Windows PowerShell 5.1 打开，保留 BOM。
# deploy.ps1 面向 pwsh 7，刻意不写进这个列表。
files = [
    root / "start.ps1",
    root / "start-dev.ps1",
    root / "pack-deploy.ps1",
]
for p in files:
    if not p.is_file():
        print("skip missing", p)
        continue
    text = p.read_text(encoding="utf-8-sig")
    p.write_text(text, encoding="utf-8-sig", newline="\r\n")
    print("wrote utf-8-sig", p.name, p.stat().st_size)
