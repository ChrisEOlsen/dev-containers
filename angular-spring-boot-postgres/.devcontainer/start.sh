#!/usr/bin/env bash
set -euo pipefail
: "${PASSWORD:?Set CODE_SERVER_PASSWORD in the ignored .env}"
mkdir -p "$HOME/.local/share/code-server/extensions" "$HOME/.local/share/code-server/User" "$HOME/.m2" "$HOME/.codex"
for extension in /opt/extensions/*.vsix; do code-server --install-extension "$extension" >/dev/null; done
# Versioned settings, persistent user state; auth credentials remain runtime-only.
cp /workspace/app/.vscode/settings.json "$HOME/.local/share/code-server/User/settings.json"
exec code-server --bind-addr 0.0.0.0:5678 --auth password --disable-telemetry /workspace/app
