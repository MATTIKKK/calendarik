import os, time, requests
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings

router = APIRouter()

@router.get("/token")
def speech_token():
    key    = settings.AZURE_SPEECH_KEY
    region = settings.AZURE_SPEECH_REGION
    print("AZURE_SPEECH_KEY =", os.getenv("AZURE_SPEECH_KEY"))

    # 1) проверка переменных окружения
    if not key:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "AZURE_SPEECH_KEY env not set")
    if not region:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "AZURE_SPEECH_REGION env not set")

    url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"

    try:
        resp = requests.post(
            url,
            headers={
                "Ocp-Apim-Subscription-Key": key,
                "Content-Length": "0"              # Azure рекомендует
            },
            timeout=5
        )
    except requests.Timeout:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT,
                            "Azure STS timeout")

    if resp.status_code != 200:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY,
                            f"Azure STS error ({resp.status_code})")

    return {
        "token": resp.text,
        "region": region,
        "expires_at": int(time.time()) + 540   # ~9 мин
    }
