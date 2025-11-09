from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

print("✅ Loaded .env from:", BASE_DIR / ".env")
print("✅ OPENAI_API_KEY starts with:", settings.openai_api_key[:8])
