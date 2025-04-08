import asyncio
import pytest
import aiosqlite
from fastapi.testclient import TestClient
from typing import AsyncGenerator, Generator, Dict, Any, List
import os
from passlib.context import CryptContext

from app.main import app
from app.database.database import get_pool
from app.config import settings
from app.models.user_model import User

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 테스트용 DB 파일 경로
TEST_DB_PATH = "test.db"

# 테스트용 데이터베이스 연결 함수 오버라이드
async def get_test_pool():
    """테스트용 SQLite 데이터베이스 연결 풀"""
    # SQLite 연결 생성
    conn = await aiosqlite.connect(TEST_DB_PATH)
    
    # 반환 값을 asyncpg Pool과 비슷하게 만들기 위한 래퍼
    class SQLitePool:
        async def acquire(self):
            return SQLiteConnection(conn)
        
        async def close(self):
            await conn.close()
    
    class SQLiteConnection:
        def __init__(self, conn):
            self.conn = conn
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        
        async def execute(self, query, *args):
            # PostgreSQL 문법을 SQLite 문법으로 변환
            query = query.replace("$", "?")
            query = query.replace("RETURNING id", "")  # SQLite는 RETURNING을 지원하지 않음
            query = query.replace("TIMESTAMP WITH TIME ZONE", "TIMESTAMP")
            
            cursor = await self.conn.execute(query, args)
            await self.conn.commit()
            return cursor.lastrowid
        
        async def fetchrow(self, query, *args):
            # PostgreSQL 문법을 SQLite 문법으로 변환
            query = query.replace("$", "?")
            
            cursor = await self.conn.execute(query, args)
            row = await cursor.fetchone()
            if not row:
                return None
            
            # 컬럼 이름 가져오기
            columns = [desc[0] for desc in cursor.description]
            
            # 딕셔너리로 변환
            result = {}
            for idx, value in enumerate(row):
                result[columns[idx]] = value
            
            return result
        
        async def fetch(self, query, *args):
            # PostgreSQL 문법을 SQLite 문법으로 변환
            query = query.replace("$", "?")
            
            cursor = await self.conn.execute(query, args)
            rows = await cursor.fetchall()
            
            # 컬럼 이름 가져오기
            columns = [desc[0] for desc in cursor.description]
            
            # 딕셔너리 리스트로 변환
            result = []
            for row in rows:
                row_dict = {}
                for idx, value in enumerate(row):
                    row_dict[columns[idx]] = value
                result.append(row_dict)
            
            return result
        
        async def transaction(self):
            class Transaction:
                async def __aenter__(self):
                    await conn.execute("BEGIN")
                    return conn
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    if exc_type is not None:
                        await conn.execute("ROLLBACK")
                    else:
                        await conn.execute("COMMIT")
            
            return Transaction()
    
    return SQLitePool()

# 테스트 데이터베이스 초기화
async def init_test_db():
    """테스트 데이터베이스 초기화"""
    # 이전 테스트 DB 파일이 있으면 삭제
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)
    
    # SQLite 연결
    conn = await aiosqlite.connect(TEST_DB_PATH)
    
    # 테이블 생성
    await conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_superuser INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    await conn.commit()
    await conn.close()

@pytest.fixture(scope="session")
def event_loop():
    """pytest-asyncio용 이벤트 루프 생성"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    """테스트마다 데이터베이스 초기화"""
    # 테스트 DB 초기화
    await init_test_db()
    
    # 원래 함수 백업
    original_get_pool = app.dependency_overrides.get(get_pool, get_pool)
    
    # 테스트용 함수로 오버라이드
    app.dependency_overrides[get_pool] = get_test_pool
    
    yield
    
    # 의존성 원복
    if original_get_pool == get_pool:
        del app.dependency_overrides[get_pool]
    else:
        app.dependency_overrides[get_pool] = original_get_pool
    
    # 테스트 DB 파일 삭제
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

@pytest.fixture
def client() -> Generator:
    """FastAPI 테스트 클라이언트"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def test_user() -> Dict[str, Any]:
    """테스트용 사용자 생성"""
    pool = await get_test_pool()
    async with pool.acquire() as conn:
        # 사용자 생성
        hashed_password = pwd_context.hash("testpassword")
        
        await conn.execute('''
            INSERT INTO users (email, username, hashed_password, is_active, is_superuser)
            VALUES (?, ?, ?, ?, ?)
        ''', "testuser@example.com", "testuser", hashed_password, 1, 0)
        
        # 생성된 사용자 정보 가져오기
        user_data = await conn.fetchrow('''
            SELECT id, email, username, is_active, is_superuser, created_at, updated_at
            FROM users
            WHERE email = ?
        ''', "testuser@example.com")
    
    return user_data

@pytest.fixture
async def test_user_token(client, test_user) -> str:
    """테스트 사용자의 액세스 토큰 발급"""
    response = client.post(
        "/api/users/token",
        data={
            "username": test_user["email"],
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

@pytest.fixture
def authorized_client(client, test_user_token) -> Generator:
    """인증된 테스트 클라이언트"""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_user_token}"
    }
    yield client