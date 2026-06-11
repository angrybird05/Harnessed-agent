from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    GEMINI_API_KEY: str
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REFRESH_TOKEN: str = ""
    GMAIL_SENDER_EMAIL: str = ""
    ADZUNA_APP_ID: str = ""
    ADZUNA_APP_KEY: str = ""
    # FIX MED-08: Configurable country code (us, gb, au, in, ca, de, fr, etc.)
    ADZUNA_COUNTRY: str = "gb"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    # FIX HIGH-05: Configurable resume storage path (not hardcoded to /app)
    RESUME_STORAGE_PATH: str = "/app/resumes"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
