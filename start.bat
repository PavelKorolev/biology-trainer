@echo off
echo 🚀 Запуск тренажёра...

REM переходим в папку проекта
cd /d %~dp0

echo 🔄 Обновляю код из Git...
git pull

REM если нет progress.json — создаём
if not exist progress.json (
    echo {} > progress.json
    echo 📄 Создан новый progress.json
)

echo 🛑 Останавливаю старый контейнер...
docker stop trainer >nul 2>&1
docker rm trainer >nul 2>&1

echo 🐳 Собираю Docker-образ...
docker build -t trainer .

echo ▶ Запускаю контейнер...
docker run -d ^
 -p 8000:8000 ^
 -v "%cd%\progress.json:/app/progress.json" ^
 --name trainer ^
 trainer

timeout /t 3 >nul

echo 🌍 Открываю браузер...
start http://localhost:8000/start

echo ✅ Готово
pause