"""PyInstaller runtime hook: prepare a writable data dir before main.py runs.

main.py reads/writes settings.json, strings.xml, unlocks.json and tmp_output.txt
from the current working directory. With --onefile, bundled files live under
sys._MEIPASS which is a temp folder destroyed at exit, so we copy the config
files to a stable per-user dir and chdir there.
"""
import os
import shutil
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    bundle = Path(sys._MEIPASS)
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
    else:
        base = Path.home() / ".local" / "share"
    data_dir = base / "nPhoneKIT"
    data_dir.mkdir(parents=True, exist_ok=True)

    for name in ("settings.json", "strings.xml", "unlocks.json"):
        dest = data_dir / name
        src = bundle / name
        if not dest.exists() and src.exists():
            shutil.copy2(src, dest)

    os.chdir(data_dir)
