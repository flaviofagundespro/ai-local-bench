#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

links=(
  /opt/rocm-6.1.1/bin/amdclang
  /opt/rocm-6.1.1/bin/amdclang++
  /opt/rocm-6.1.1/bin/amdclang-cl
  /opt/rocm-6.1.1/bin/amdclang-cpp
  /opt/rocm-6.1.1/bin/amdflang
  /opt/rocm-6.1.1/bin/amdlld
  /opt/rocm-6.1.1/bin/offload-arch
)

for link in "${links[@]}"; do
  if [[ -L "${link}" ]]; then
    rm -f "${link}"
  fi
done

dpkg --configure -a
apt-get install -y -f

echo
echo "ROCm LLVM links repaired. Verify with:"
echo "dpkg -l | grep -E '^(ii).*6\\.1\\.1'"
echo "rocminfo | grep -E 'gfx|Marketing Name|Name:'"
