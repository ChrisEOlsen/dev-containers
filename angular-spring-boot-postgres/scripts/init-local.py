#!/usr/bin/env python3
import os
import secrets
from pathlib import Path

p = Path(".env")
if p.exists():
    raise SystemExit(".env already exists; leaving it untouched")
s = (
    Path(".env.example")
    .read_text()
    .replace("POSTGRES_PASSWORD=", "POSTGRES_PASSWORD=" + secrets.token_hex(24))
    .replace("CODE_SERVER_PASSWORD=", "CODE_SERVER_PASSWORD=" + secrets.token_hex(24))
)
s = s.replace(
    "LOCAL_UID=1000", "LOCAL_UID=" + str(os.getuid() if os.getuid() != 0 else 1000)
)
p.write_text(s)
p.chmod(0o600)
print(
    "Created ignored .env. Open it privately to use the editor password; do not paste it into logs."
)
