"""Access-gated launcher used as the PyInstaller entry point.

Shows a Tk password prompt at startup. On success, executes main.py with
__name__ == "__main__" so its bottom-of-file bootstrap runs unchanged.

Tk is used (instead of PyQt5) to avoid creating a QApplication before main.py
instantiates its own — Qt allows only one per process.
"""
import hashlib
import hmac
import json
import runpy
import sys
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, simpledialog

PBKDF2_ITERATIONS = 600_000
MAX_ATTEMPTS = 3


def _bundle_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _verify(code: str, salt_hex: str, expected_hex: str) -> bool:
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        code.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ITERATIONS,
    ).hex()
    return hmac.compare_digest(derived, expected_hex)


def _gate() -> bool:
    bundle = _bundle_dir()
    hash_file = bundle / "access_hash.json"
    root = tk.Tk()
    root.withdraw()
    try:
        if sys.platform == "win32":
            icon = bundle / "favicon.ico"
            if icon.exists():
                try:
                    root.iconbitmap(default=str(icon))
                except tk.TclError:
                    pass

        if not hash_file.exists():
            messagebox.showerror(
                "nPhoneKIT", "Build invalide : access_hash.json manquant."
            )
            return False

        data = json.loads(hash_file.read_text(encoding="utf-8"))
        salt_hex, expected_hex = data["salt"], data["hash"]

        expires_at = data.get("expires_at")
        if expires_at:
            try:
                deadline = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            except ValueError:
                messagebox.showerror("nPhoneKIT", "Build invalide : expiration illisible.")
                return False
            if datetime.now(timezone.utc) >= deadline:
                messagebox.showerror(
                    "nPhoneKIT",
                    f"Build expiré (limite : {deadline.strftime('%Y-%m-%d %H:%M UTC')}).\n"
                    "Demandez une nouvelle version.",
                )
                return False

        for attempt in range(MAX_ATTEMPTS):
            prompt = (
                "Entrez le code d'accès :"
                if attempt == 0
                else f"Code invalide. Essai {attempt + 1}/{MAX_ATTEMPTS} :"
            )
            code = simpledialog.askstring(
                "nPhoneKIT — Code d'accès", prompt, show="*", parent=root
            )
            if code is None:
                return False
            if _verify(code, salt_hex, expected_hex):
                return True

        messagebox.showerror("nPhoneKIT", "Trop d'essais invalides. Fermeture.")
        return False
    finally:
        root.destroy()


def main() -> int:
    if not _gate():
        return 1
    runpy.run_path(str(_bundle_dir() / "main.py"), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
