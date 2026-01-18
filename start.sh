#!/bin/zsh
set -e

IMAGE=trainer
CONTAINER=trainer
PORT=8000

cd "$(dirname "$0")"

echo "== Pull latest code =="
git pull

echo "== Ensure local progress.json exists =="
test -f progress.json || echo "{}" > progress.json

echo "== Stop/remove old container =="
docker stop $CONTAINER 2>/dev/null || true
docker rm $CONTAINER 2>/dev/null || true

echo "== Build image (no cache) =="
docker build --no-cache -t $IMAGE .

echo "== Run container =="
docker run -d -p ${PORT}:8000 --name $CONTAINER \
  -v "$(pwd)/progress.json:/app/progress.json" \
  $IMAGE

echo "== Open in browser =="
open http://localhost:${PORT}/start