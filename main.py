from fastapi import FastAPI, Request, HTTPException, Response
import httpx
import os

app = FastAPI()

# Адрес Agnes AI, к которому будем перенаправлять запросы
AGNES_API_BASE = "https://apihub.agnes-ai.com"

# Получаем ключ из переменных окружения
AGNES_API_KEY = os.getenv("AGNES_API_KEY")

if not AGNES_API_KEY:
    raise ValueError("AGNES_API_KEY не задан в переменных окружения")

# Создаём HTTP-клиент для переадресации
client = httpx.AsyncClient(base_url=AGNES_API_BASE, timeout=300.0)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """Универсальный прокси для Agnes AI"""
    
    # Формируем URL для перенаправления
    target_url = f"/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Копируем заголовки, подменяя авторизацию
    headers = dict(request.headers)
    headers["Authorization"] = f"Bearer {AGNES_API_KEY}"
    headers.pop("host", None)  # Убираем host, чтобы не мешал

    # Читаем тело запроса
    body = await request.body()

    # Отправляем запрос к Agnes AI
    try:
        agnes_response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка при запросе к Agnes AI: {e}")

    # Возвращаем ответ Agnes AI клиенту
    return Response(
        content=agnes_response.content,
        status_code=agnes_response.status_code,
        headers=dict(agnes_response.headers),
    )


@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()