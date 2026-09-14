FROM python:3.12-alpine

WORKDIR /app

RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -D -s /bin/sh appuser

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup main.py .

USER 1000:1000

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
