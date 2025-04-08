import pytest
import asyncio
from app.repositories.user_repository import UserRepository
from app.models.user_model import UserCreate

@pytest.mark.asyncio
async def test_create_user():
    """사용자 생성 테스트"""
    # Given
    user_data = UserCreate(
        email="new_user@example.com",
        username="newuser",
        password="password123"
    )
    
    # When
    user = await UserRepository.create_user(user_data)
    
    # Then
    assert user is not None
    assert user.email == user_data.email
    assert user.username == user_data.username
    assert hasattr(user, "id")
    assert user.is_active is True

@pytest.mark.asyncio
async def test_get_user_by_id(test_user):
    """ID로 사용자 조회 테스트"""
    # When
    user = await UserRepository.get_user_by_id(test_user["id"])
    
    # Then
    assert user is not None
    assert user.id == test_user["id"]
    assert user.email == test_user["email"]
    assert user.username == test_user["username"]

@pytest.mark.asyncio
async def test_get_user_by_email(test_user):
    """이메일로 사용자 조회 테스트"""
    # When
    user = await UserRepository.get_user_by_email(test_user["email"])
    
    # Then
    assert user is not None
    assert user.id == test_user["id"]
    assert user.email == test_user["email"]
    assert hasattr(user, "hashed_password")

@pytest.mark.asyncio
async def test_get_user_by_username(test_user):
    """사용자 이름으로 사용자 조회 테스트"""
    # When
    user = await UserRepository.get_user_by_username(test_user["username"])
    
    # Then
    assert user is not None
    assert user.id == test_user["id"]
    assert user.username == test_user["username"]

@pytest.mark.asyncio
async def test_get_all_users(test_user):
    """모든 사용자 조회 테스트"""
    # When
    users = await UserRepository.get_all_users()
    
    # Then
    assert len(users) >= 1
    assert any(u.id == test_user["id"] for u in users)

@pytest.mark.asyncio
async def test_update_user(test_user):
    """사용자 정보 업데이트 테스트"""
    # Given
    from app.models.user_model import UserUpdate
    update_data = UserUpdate(username="updated_username")
    
    # When
    updated_user = await UserRepository.update_user(test_user["id"], update_data)
    
    # Then
    assert updated_user is not None
    assert updated_user.id == test_user["id"]
    assert updated_user.username == "updated_username"
    assert updated_user.email == test_user["email"]  # 변경하지 않은 필드는 그대로

@pytest.mark.asyncio
async def test_delete_user(test_user):
    """사용자 삭제 테스트"""
    # When
    result = await UserRepository.delete_user(test_user["id"])
    deleted_user = await UserRepository.get_user_by_id(test_user["id"])
    
    # Then
    assert result is True
    assert deleted_user is None

@pytest.mark.asyncio
async def test_verify_user():
    """사용자 인증 테스트"""
    # Given
    user_data = UserCreate(
        email="verify@example.com",
        username="verifyuser",
        password="verifypass123"
    )
    await UserRepository.create_user(user_data)
    
    # When - 올바른 비밀번호
    verified_user = await UserRepository.verify_user(user_data.email, user_data.password)
    
    # Then
    assert verified_user is not None
    assert verified_user.email == user_data.email
    assert not hasattr(verified_user, "hashed_password")  # 비밀번호 해시는 포함되지 않아야 함

@pytest.mark.asyncio
async def test_verify_user_wrong_password():
    """잘못된 비밀번호로 사용자 인증 테스트"""
    # Given
    user_data = UserCreate(
        email="verify2@example.com",
        username="verifyuser2",
        password="correctpass"
    )
    await UserRepository.create_user(user_data)
    
    # When - 잘못된 비밀번호
    verified_user = await UserRepository.verify_user(user_data.email, "wrongpass")
    
    # Then
    assert verified_user is None