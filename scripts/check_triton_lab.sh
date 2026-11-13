#!/usr/bin/env bash
# Read-only Day 4 startup/readiness diagnostic (no Docker start/restart).
set -u
echo "=== HOST ==="
hostname
uptime
echo "=== DOCKER SERVICE ==="
sudo systemctl is-active docker || true
echo "=== TRITON CONTAINER ==="
sudo docker ps -a --filter name=triton-cpu || true
echo "=== TRITON READY ==="
curl -sS -o /dev/null -w 'Model HTTP Status: %{http_code}\n' \
  http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/ready || true
echo "=== VM MEMORY ==="
free -h
echo "=== PYTHON PACKAGES ==="
"$HOME/dragonstorm-lab/.venv-onnx-inspect/bin/python" - <<'PY'
import importlib.util
for module in ("numpy", "onnx", "PIL", "cv2", "scipy"):
    print(module, "installed" if importlib.util.find_spec(module) else "NOT INSTALLED")
PY
echo "READ-ONLY LAB CHECK COMPLETE"
