#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

printf '%s\n' \
  'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.1.1 jammy main' \
  > /etc/apt/sources.list.d/rocm.list

apt-get update
apt-get install -y \
  hip-runtime-amd6.1.1 \
  hipcc6.1.1 \
  hipblas-dev6.1.1 \
  rocblas-dev6.1.1 \
  rocm-device-libs6.1.1 \
  rocminfo6.1.1 \
  rocm-llvm-dev6.1.1

ln -sf /usr/bin/amdgpu-install /usr/bin/amdgpu-uninstall

echo
echo "Minimal ROCm 6.1.1 build packages installed. Re-open the shell or reboot before rebuilding llama.cpp."
echo "Then verify with: rocminfo | rg 'gfx|Marketing Name|Name:'"
