from fastapi import FastAPI, Request, HTTPException, Response
import httpx
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

AGNES_API_BASE = "https://apihub.agnes-ai.com"
AGNES_API_KEY = os.getenv("AGNES_API_KEY")

if not AGNES_API_KEY:
    raise ValueError("AGNES_API_KEY не задан")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    # Формируем целевой URL
    target_url = f"{AGNES_API_BASE}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Явно задаём заголовки, которые Cloudflare пропускает
    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://apihub.agnes-ai.com",
        "Referer": "https://apihub.agnes-ai.com/",
    }

    body = await request.body()
    logger.info(f"→ {request.method} {target_url}")

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {e}")
            raise HTTPException(status_code=502, detail=str(e))

    logger.info(f"← {resp.status_code} {target_url}")

    # Возвращаем ответ Agnes AI
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers={
            "Content-Type": resp.headers.get("Content-Type", "application/json"),
            "Access-Control-Allow-Origin": "*",
        },
    )
