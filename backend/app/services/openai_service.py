import os
from openai import AsyncAzureOpenAI
from app.core.config import settings

client = AsyncAzureOpenAI(
    azure_endpoint=settings.ENDPOINT_URL,
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2025-01-01-preview",
)

async def ask_gpt(messages: list[dict], model: str = settings.DEPLOYMENT_NAME):
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=800,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
    return response.choices[0].message.content
