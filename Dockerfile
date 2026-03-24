FROM python:3.12-slim

WORKDIR /app

# curl нужен для HEALTHCHECK
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# непривилегированный пользователь
RUN adduser --disabled-password --gecos "" appuser

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код и шаблоны
COPY script.py .
COPY templates ./templates

# ВАЖНО: оба файла вопросов
COPY questions_all.json .
COPY questions_allChemistry.json .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/start || exit 1

CMD ["uvicorn", "script:app", "--host", "0.0.0.0", "--port", "8000"]
