#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" == "--install-tools" ]]; then
  apt-get -o Acquire::Retries=3 update
  apt-get install -y binutils ca-certificates curl g++ git python3 unzip
fi
python3 "$repo/scripts/build.py" --platform linux --skip-studio
