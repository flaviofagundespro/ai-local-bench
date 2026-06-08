#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

apt-get update
apt-get install -y \
  -o Dpkg::Options::="--force-overwrite" \
  rocm-core6.1.1 \
  rocm-llvm6.1.1

apt-get install -y -f

echo
echo "ROCm 6.1.1 partial install repaired. Verify with:"
echo "dpkg -l | grep -E '^(ii).*6\\.1\\.1'"
echo "rocminfo | grep -E 'gfx|Marketing Name|Name:'"
