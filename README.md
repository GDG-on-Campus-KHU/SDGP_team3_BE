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