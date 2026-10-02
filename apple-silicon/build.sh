#!/usr/bin/env bash
# Build apple-silicon/alignmutex.so (x86-64 Linux), once. Needs only Docker.
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
[ -f "$D/alignmutex.so" ] && [ "$D/alignmutex.so" -nt "$D/alignmutex.c" ] && exit 0
docker run --rm --platform linux/amd64 -v "$D:/w" -w /w gcc:13 \
    gcc -O2 -shared -fPIC -o alignmutex.so alignmutex.c -ldl -lpthread
echo "built $D/alignmutex.so"
