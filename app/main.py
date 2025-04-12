import asyncio

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.controllers import user_controller
from app.database.database import init_db

# google control 라우터
from app.controllers import google_controller

from starlette.middleware.sessions import SessionMiddleware


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# 세션 미들웨어 (authlib 사용)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    same_site="lax",
    https_only=False
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # 프로덕션에서는 실제 프론트엔드 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(user_controller.router)
app.include_router(google_controller.router)

@app.get("/")
def read_root() -> dict:
    """루트 엔드포인트"""
    return {"message": "Welcome to FastAPI PostgreSQL Project API"}


@app.get("/health")  # localhost:80/health
def health_check() -> dict:
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event() -> None:
    """애플리케이션 시작 시 이벤트"""
    # 데이터베이스 초기화
    await init_db()
    print("Application started, database initialized")


if __name__ == "__main__":
    import uvicorn  # 웹 애플리케이션 프레임워크.

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
