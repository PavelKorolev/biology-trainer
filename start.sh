#!/bin/zsh

echo "🚀 Запуск тренажёра..."

cd "$(dirname "$0")"

echo "🔄 Обновление проекта"
git pull

echo "🛑 Останавливаю старый контейнер"
docker stop trainer 2>/dev/null
docker rm trainer 2>/dev/null

echo "🐳 Сборка Docker"
docker build -t trainer .

echo "▶️ Запуск контейнера"
docker run -d \
  -p 8000:8000 \
  -v "$(pwd)/progress.json:/app/progress.json" \
  --name trainer \
  trainer

sleep 2

echo "🌍 Открываю браузер"
explorer.exe http://localhost:8000/start