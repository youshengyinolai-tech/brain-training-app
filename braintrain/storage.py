"""生成したPDFの保存先と、ファイルを開く処理。"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_output_dir():
    out = Path.home() / "脳トレメーカー" / "印刷用データ"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_output_path(label):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return get_output_dir() / f"{label}_{ts}.pdf"


def open_path(path):
    path = str(path)
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606 (Windows専用API)
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)
