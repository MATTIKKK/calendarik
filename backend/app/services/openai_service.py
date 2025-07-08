import os
from openai import AsyncAzureOpenAI
from app.core.config import settings
from typing import Optional, List

client = AsyncAzureOpenAI(
    azure_endpoint=settings.ENDPOINT_URL,
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2025-01-01-preview",
)

async def ask_gpt(
    messages: list[dict],
    model: str = settings.DEPLOYMENT_NAME,
    temperature: float = 1.0,
    max_tokens: int = 800,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    stop: Optional[List[str]] = None,
    stream: bool = False,
):
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
        stream=stream
    )
    return response.choices[0].message.content