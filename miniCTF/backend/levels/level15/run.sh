#!/usr/bin/env bash
set -e
PORT=9015
IMAGE=ctf-lab-11-15

docker rm -f $IMAGE-l15 >/dev/null 2>&1 || true
docker run --name $IMAGE-l15 -p ${PORT}:8000 $IMAGE
echo "[*] Open: http://localhost:${PORT}/level/15"