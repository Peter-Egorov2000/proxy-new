FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости от root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создаём непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash appuser

# Копируем код и даём права пользователю
COPY --chown=appuser:appuser main.py .

# Переключаемся на непривилегированного пользователя
USER appuser

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
