#!/usr/bin/env python3
import asyncio
import glob
import os
import sys

import asyncpg

# 현재 파일 기준 프로젝트 루트 디렉토리 sys.path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.config import settings


async def run_migration(conn: asyncpg.Connection, migration_file: str) -> None:
    """단일 마이그레이션 파일 실행"""
    print(f"적용 중: {migration_file}")
    with open(migration_file, "r") as f:
        sql = f.read()
        await conn.execute(sql)


async def get_applied_migrations(conn: asyncpg.Connection) -> set:
    """이미 적용된 마이그레이션 조회"""
    # 마이그레이션 테이블이 없으면 생성
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # 적용된 마이그레이션 목록 조회
    rows = await conn.fetch("SELECT filename FROM migrations")
    return {row["filename"] for row in rows}


async def mark_migration_applied(conn: asyncpg.Connection, filename: str) -> None:
    """마이그레이션을 적용됨으로 표시"""
    await conn.execute(
        "INSERT INTO migrations (filename) VALUES ($1)", os.path.basename(filename)
    )


async def run_migrations() -> None:
    """데이터베이스 마이그레이션 실행"""
    print("데이터베이스 마이그레이션 시작")

    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(settings.DATABASE_URL)

        # 적용된 마이그레이션 목록 조회
        applied_migrations = await get_applied_migrations(conn)

        # 마이그레이션 파일 경로
        migration_path = os.path.join(os.path.dirname(__file__), "sql")
        migration_files = sorted(glob.glob(os.path.join(migration_path, "*.sql")))

        # 적용되지 않은 마이그레이션 실행
        for migration_file in migration_files:
            filename = os.path.basename(migration_file)
            if filename not in applied_migrations:
                try:
                    # 트랜잭션 내에서 마이그레이션 실행
                    async with conn.transaction():
                        await run_migration(conn, migration_file)
                        await mark_migration_applied(conn, migration_file)
                    print(f"✅ 마이그레이션 성공: {filename}")
                except Exception as e:
                    print(f"❌ 마이그레이션 실패: {filename}")
                    print(f"오류: {e}")
                    # 실패한 마이그레이션이 있으면 중단
                    sys.exit(1)
            else:
                print(f"⏭️  이미 적용됨: {filename}")

        print("데이터베이스 마이그레이션 완료")
    except Exception as e:
        print(f"마이그레이션 오류: {e}")
        sys.exit(1)
    finally:
        # 연결 종료
        if "conn" in locals():
            await conn.close()


if __name__ == "__main__":
    # 마이그레이션 실행
    asyncio.run(run_migrations())
