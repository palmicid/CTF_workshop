#!/usr/bin/env bash
set -e
PORT=9012
IMAGE=ctf-lab-11-15

echo "[*] Using shared CTF Lab (build lives in level11/docker)."
echo "[*] If image not built yet, run Level 11 script first OR build with:"
echo "    docker build -t $IMAGE ../level11/docker"

docker rm -f $IMAGE-l12 >/dev/null 2>&1 || true
docker run --name $IMAGE-l12 -p ${PORT}:8000 $IMAGE
echo "[*] Open: http://localhost:${PORT}/level/12"