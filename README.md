## SDGP-Team3-Backend & AI
### Team Members
- ET
- JH

### Project Description
- 샘플

## Project Structure

```
SDGP_team3_BE
├─ .pre-commit-config.yaml
├─ .python-version
├─ Dockerfile
├─ README.md
├─ app
│  ├─ __init__.py
│  ├─ config.py
│  ├─ controllers
│  │  ├─ __init__.py
│  │  └─ user_controller.py
│  ├─ database
│  │  ├─ __init__.py
│  │  └─ database.py
│  ├─ dto
│  │  ├─ __init__.py
│  │  └─ user_dto.py
│  ├─ main.py
│  ├─ models
│  │  ├─ __init__.py
│  │  └─ user_model.py
│  ├─ repositories
│  │  ├─ __init__.py
│  │  └─ user_repository.py
│  └─ services
│     ├─ __init__.py
│     └─ user_service.py
├─ docker-compose.yml
├─ migrations
│  ├─ migrate.py
│  └─ sql
│     ├─ 001_create_users_table.sql
│     └─ 002_add_is_superuser_column.sql
├─ poetry.lock
├─ pyproject.toml
└─ test
   ├─ __init__.py
   ├─ conftest.py
   ├─ test_controllers
   │  ├─ __init__.py
   │  └─ test_user_controller.py
   ├─ test_repositories
   │  ├─ __init__.py
   │  └─ test_user_repository.py
   └─ test_services
      ├─ __init__.py
      └─ test_user_service.py

```

## 시작
```bash
# 가상환경 생성
poetry install
# 가상환경 활성화
poetry shell
# 커밋 전 자동으로 코드 스타일 검사 및 수정
poetry run pre-commit install
poetry run pre-commit run --all-files
# 커밋 전 정적 타입 stub 설치
poetry run mypy --install-types
# 서버 실행
uvicorn app.main:app
```
