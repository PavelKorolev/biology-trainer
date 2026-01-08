FROM python:3.12-slim

WORKDIR /app

# 1️⃣ Копируем requirements
COPY requirements.txt .

# 2️⃣ Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 3️⃣ Копируем код и данные
COPY script.py .
COPY questions_all.json .
COPY templates ./templates

EXPOSE 8000

CMD ["uvicorn", "script:app", "--host", "0.0.0.0", "--port", "8000"]
