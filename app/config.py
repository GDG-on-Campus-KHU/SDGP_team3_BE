import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# .env 파일에서 환경변수 로드
env_filename = os.getenv("ENV_FILENAME", ".env.test")
if "test" not in env_filename:
    print(f"[WARNING] test 환경이 아닙니다! 파일 이름: {env_filename}")
    load_dotenv(env_filename)
else:
    print(f"[INFO] test 환경입니다! 파일 이름: {env_filename}")
    load_dotenv(env_filename)


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

    print("DATABASE_URL:", DATABASE_URL)

    # 테스트용 SQLite 데이터베이스 URL
    TEST_DATABASE_URL: str = "sqlite:///./test.db"

    # JWT 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY") or "this-is-a-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # GOOGLE OAuth 설정
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID") or ""
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET") or ""
    GOOGLE_REDIRECT_URI: str = (
        os.getenv("GOOGLE_REDIRECT_URI") or "http://localhost:8000/api/google/callback"
    )

    # SESSION 미들웨어 설정
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "default-secret-key")

    # Gemini
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


settings = Settings()
