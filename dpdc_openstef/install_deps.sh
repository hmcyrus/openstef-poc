#!/usr/bin/env sh
# Install Python dependencies: try Poetry first, fall back to pip.
set -e

# Always run from within dpdc_openstef/ regardless of caller's working directory.
cd "$(dirname "$0")"

if ! command -v poetry >/dev/null 2>&1; then
    echo "[install_deps] Poetry not found. Attempting to install via pip..."
    pip install --quiet poetry || true
fi

if command -v poetry >/dev/null 2>&1; then
    echo "[install_deps] Using Poetry..."
    poetry install --no-root
else
    echo "[install_deps] Poetry unavailable. Falling back to pip..."
    pip install -r requirements.txt
fi
