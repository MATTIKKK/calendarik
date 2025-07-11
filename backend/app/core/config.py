from pydantic_settings import BaseSettings
from pydantic import EmailStr, PostgresDsn, validator
from typing import Optional


class Settings(BaseSettings):
    # === Database ===
    DATABASE_URL: PostgresDsn

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            return v
        return str(v)

    # === Security ===
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # === Frontend ===
    FRONTEND_URL: str = "http://localhost:5173"

    # === OpenAI ===
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 500
    
    AZURE_SPEECH_KEY: str
    AZURE_SPEECH_REGION: str

    ENDPOINT_URL: str
    AZURE_OPENAI_API_KEY: str
    DEPLOYMENT_NAME: str = "gpt-4.1"

    # === Email settings (for future use) ===
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
