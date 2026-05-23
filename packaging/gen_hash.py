"""Generate packaging/access_hash.json from the ACCESS_CODE env var.

Adds a 24-hour expiration timestamp (UTC) past which the launcher refuses
to start. The validity window can be overridden with EXPIRES_HOURS.
"""
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone

code = os.environ.get("ACCESS_CODE", "").strip()
if not code:
    sys.stderr.write("ACCESS_CODE env var is empty\n")
    sys.exit(1)

hours = float(os.environ.get("EXPIRES_HOURS", "24"))
salt = secrets.token_bytes(16)
digest = hashlib.pbkdf2_hmac("sha256", code.encode("utf-8"), salt, 600_000)
expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)

payload = {
    "salt": salt.hex(),
    "hash": digest.hex(),
    "expires_at": expires_at.isoformat(),
}

out_path = os.environ.get("OUT_PATH", "packaging/access_hash.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(payload, f)

sys.stderr.write(f"access_hash.json written -> {out_path} (expires {expires_at.isoformat()})\n")
