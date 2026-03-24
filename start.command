#!/bin/bash
set -e

# переходим в папку проекта (работает даже если запускать через Alias с рабочего стола)
cd "$(dirname "$0")"

IMAGE=trainer
CONTAINER=trainer
PORT=8000

echo "== Проверяю Docker =="
if ! docker info > /dev/null 2>&1; then
    echo ""
    echo "❌ Docker не запущен. Открой Docker Desktop и подожди пока он стартует, затем повтори."
    read -p "Нажми Enter для выхода..."
    exit 1
fi

echo "== Обновляю проект =="
git pull 2>/dev/null || echo "⚠️  git pull не удался — продолжаю с текущей версией"

echo "== Создаю progress.json если нет =="
test -f progress.json || echo "{}" > progress.json

echo "== Останавливаю старый контейнер =="
docker stop $CONTAINER 2>/dev/null || true
docker rm $CONTAINER 2>/dev/null || true

echo "== Собираю образ =="
docker build -t $IMAGE .

echo "== Запускаю контейнер =="
docker run -d \
  -p ${PORT}:8000 \
  --name $CONTAINER \
  -v "$(pwd)/progress.json:/app/progress.json" \
  $IMAGE

echo "== Жду запуска =="
sleep 3

echo "== Открываю браузер =="
open http://localhost:${PORT}/start

echo ""
echo "✅ Тренажёр запущен! Можешь закрыть это окно."
