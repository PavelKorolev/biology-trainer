FROM python:3.12-slim

WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код и шаблоны
COPY script.py .
COPY templates ./templates

# ВАЖНО: оба файла вопросов
COPY questions_all.json .
COPY questions_allChemistry.json .

EXPOSE 8000

CMD ["uvicorn", "script:app", "--host", "0.0.0.0", "--port", "8000"]