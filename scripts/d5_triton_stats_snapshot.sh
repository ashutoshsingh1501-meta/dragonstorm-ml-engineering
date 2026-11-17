#!/usr/bin/env bash
# DragonStorm D5-01 — read-only Triton model statistics snapshot.
# Authored 2026-11-17; NOT EXECUTED/validated on Azure VM yet.
# Copies are separate: GitHub source != VM-local shell script.
# Usage: bash d5_triton_stats_snapshot.sh before
#        bash d5_triton_stats_snapshot.sh after
# Requirement: Triton already running on 127.0.0.1:8000; curl and Python venv available.
set -euo pipefail

label="${1:-snapshot}"
case "$label" in
  before|after|snapshot) ;;
  *) echo 'Label must be before, after or snapshot' >&2; exit 2 ;;
esac

lab="${HOME}/dragonstorm-lab"
python="${lab}/.venv-onnx-inspect/bin/python"
model="ssd_mobilenet_v1_12"
url="http://127.0.0.1:8000/v2/models/${model}/stats"
dir="${lab}/d5-profiling"
mkdir -p "$dir"
stamp="$(date -u +'%Y%m%dT%H%M%SZ')"
file="${dir}/triton-stats-${label}-${stamp}.json"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

echo "=== D5 TRITON MODEL STATISTICS SNAPSHOT ==="
echo "UTC stamp: $stamp"
echo "Label: $label"
echo "URL: $url"
code="$(curl --max-time 20 -sS -w '%{http_code}' -o "$tmp" "$url")" || {
  echo "Failed to query Triton. Check readiness; model statistics are not confirmed." >&2
  cat "$tmp" >&2 || true
  exit 1
}
echo "HTTP status: $code"
if [[ "$code" != "200" ]]; then
  echo "Triton stats request was not successful:" >&2
  cat "$tmp" >&2
  exit 1
fi

# Verify JSON before preserving it; do not silently treat malformed payloads as valid.
"$python" -m json.tool "$tmp" >/dev/null
cp "$tmp" "$file"
echo "Snapshot saved: $file"
"$python" -m json.tool "$file"
echo "D5 MODEL STATISTICS SNAPSHOT CAPTURED (interpretation pending)"
