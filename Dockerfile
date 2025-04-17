# Python 3.9-slim 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 타임존 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Poetry 가상환경 생성 방지
RUN poetry config virtualenvs.create false

# pyproject.toml과 poetry.lock 복사
COPY pyproject.toml poetry.lock* /app/

# 소스 코드 복사
COPY . .

# 의존성 설치
RUN poetry install --no-interaction --no-ansi --no-root

# 마이그레이션 스크립트에 실행 권한 부여
RUN chmod +x migrations/migrate.py

# 컨테이너 실행 시 명령어
CMD ["bash", "-c", "python -m migrations.migrate && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

# 의존성 설치 (현재 프로젝트는 설치하지 않음)
RUN poetry install --no-interaction --no-ansi --no-root
