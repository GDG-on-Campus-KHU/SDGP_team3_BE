import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# .env 파일에서 환경변수 로드
load_dotenv(".env.example")


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI PostgreSQL Project"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "fastapi_db")

    # DSN 형식의 데이터베이스 URL
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # 테스트용 SQLite 데이터베이스 URL
    TEST_DATABASE_URL: str = "sqlite:///./test.db"

    # JWT 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
