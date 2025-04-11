import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import asyncpg

from app.config import settings

# 전역 연결 풀
pool = None


async def get_pool() -> asyncpg.Pool:
    """비동기 데이터베이스 연결 풀 가져오기"""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL, min_size=5, max_size=20, record_class=dict
        )
    return pool


async def get_db() -> AsyncGenerator[asyncpg.Pool, None]:
    """FastAPI 의존성 주입을 위한 데이터베이스 연결 제공"""
    pool = await get_pool()
    try:
        yield pool
    finally:
        pass  # 연결 풀은 앱이 종료될 때 닫힙니다


async def execute_query(query: str, values: Optional[tuple] = None) -> Any:
    """
    SQL 쿼리 실행 (INSERT, UPDATE, DELETE)
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if values:
            return await conn.execute(query, *values)
        return await conn.execute(query)


async def fetch_one(
    query: str, values: Optional[tuple] = None
) -> Union[Any, Dict[str, Any]]:
    """
    단일 레코드 조회
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if values:
            return await conn.fetchrow(query, *values)
        return await conn.fetchrow(query)


async def fetch_all(
    query: str, values: Optional[tuple] = None
) -> Union[Any, List[Dict[str, Any]]]:
    """
    여러 레코드 조회
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if values:
            return await conn.fetch(query, *values)
        return await conn.fetch(query)


async def execute_many(query: str, values: List[tuple]) -> Any:
    """
    여러 쿼리 일괄 실행
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        # 트랜잭션 사용 -> 이제 Atomic하게 처리됨!
        # async with conn.transaction():
        #     # executemany 대신 prepare와 execute 조합 사용
        #     stmt = await conn.prepare(query)
        #     await asyncio.gather(*[stmt.execute(*value) for value in values])
        return await conn.executemany(query, *values)


async def init_db() -> None:
    """
    데이터베이스 초기화 함수
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # 유저 테이블 생성
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_superuser BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
