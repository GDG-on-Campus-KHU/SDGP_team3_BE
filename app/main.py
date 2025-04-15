import asyncio
from typing import Any, Optional, cast

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings

# google control 라우터
from app.controllers import google_controller, user_controller
from app.database.database import init_db

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# 세션 미들웨어 (authlib 사용)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    same_site="lax",
    https_only=False,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 실제 프론트엔드 도메인으로 제한
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


# swagger에서 bearer token 인증 추가
from fastapi.openapi.utils import get_openapi


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return cast(dict[str, Any], app.openapi_schema)

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="FastAPI Google OAuth + JWT 기반 인증 API",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "security" not in method:
                method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return cast(dict[str, Any], app.openapi_schema)


app.openapi = custom_openapi  # type : ignore[assignment]


if __name__ == "__main__":
    import uvicorn  # 웹 애플리케이션 프레임워크.

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
