#!/usr/bin/env bash
set -euo pipefail
grep -R "TODO(student)" -n \
  --exclude-dir="__pycache__" \
  --exclude-dir="*.egg-info" \
  src tests docs || true
