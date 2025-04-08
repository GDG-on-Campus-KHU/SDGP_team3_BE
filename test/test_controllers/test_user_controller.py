import pytest
import json
from fastapi.testclient import TestClient

def test_create_user(client):
    """사용자 생성 엔드포인트 테스트"""
    # Given
    user_data = {
        "email": "controller_test@example.com",
        "username": "controlleruser",
        "password": "controllerpass123"
    }
    
    # When
    response = client.post("/api/users/", json=user_data)
    
    # Then
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

def test_create_duplicate_user(client):
    """중복 사용자 생성 시 에러 반환 테스트"""
    # Given - 첫 번째 사용자 생성
    user_data = {
        "email": "duplicate@example.com",
        "username": "duplicateuser",
        "password": "duplicatepass123"
    }
    client.post("/api/users/", json=user_data)
    
    # When - 동일한 이메일로 다시 생성 시도
    response = client.post("/api/users/", json=user_data)
    
    # Then
    assert response.status_code == 400
    assert "이미 존재하는" in response.json()["detail"]

def test_get_all_users(authorized_client):
    """모든 사용자 조회 엔드포인트 테스트"""
    # When
    response = authorized_client.get("/api/users/")
    
    # Then
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
def test_get_current_user(authorized_client):
    """현재 로그인한 사용자 정보 조회 테스트"""
    # When
    response = authorized_client.get("/api/users/me")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "username" in data

def test_get_user(authorized_client, test_user):
    """ID로 사용자 조회 엔드포인트 테스트"""
    # When
    response = authorized_client.get(f"/api/users/{test_user['id']}")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user["id"]
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]

def test_get_nonexistent_user(authorized_client):
    """존재하지 않는 사용자 조회 시 404 반환 테스트"""
    # When
    response = authorized_client.get("/api/users/999")  # 존재하지 않는 ID
    
    # Then
    assert response.status_code == 404
    assert "찾을 수 없습니다" in response.json()["detail"]

def test_update_user(authorized_client, test_user):
    """사용자 정보 업데이트 엔드포인트 테스트"""
    # Given
    update_data = {
        "username": "controller_updated"
    }
    
    # When
    response = authorized_client.put(f"/api/users/{test_user['id']}", json=update_data)
    
    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user["id"]
    assert data["username"] == update_data["username"]
    assert data["email"] == test_user["email"]  # 변경하지 않은 필드는 그대로

def test_update_nonexistent_user(authorized_client):
    """존재하지 않는 사용자 업데이트 시 404 반환 테스트"""
    # Given
    update_data = {
        "username": "nonexistent_updated"
    }
    
    # When
    response = authorized_client.put("/api/users/999", json=update_data)  # 존재하지 않는 ID
    
    # Then
    assert response.status_code == 404
    assert "찾을 수 없습니다" in response.json()["detail"]

def test_delete_user(authorized_client, test_user):
    """사용자 삭제 엔드포인트 테스트"""
    # When
    response = authorized_client.delete(f"/api/users/{test_user['id']}")
    
    # Then
    assert response.status_code == 204
    
    # 삭제 확인
    get_response = authorized_client.get(f"/api/users/{test_user['id']}")
    assert get_response.status_code == 404

def test_login(client):
    """사용자 로그인 엔드포인트 테스트"""
    # Given - 사용자 생성
    user_data = {
        "email": "login_test@example.com",
        "username": "loginuser",
        "password": "loginpass123"
    }
    client.post("/api/users/", json=user_data)
    
    # When - 로그인
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/users/login", json=login_data)
    
    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data

def test_login_wrong_password(client):
    """잘못된 비밀번호로 로그인 시 401 반환 테스트"""
    # Given - 사용자 생성
    user_data = {
        "email": "login_test2@example.com",
        "username": "loginuser2",
        "password": "loginpass123"
    }
    client.post("/api/users/", json=user_data)
    
    # When - 잘못된 비밀번호로 로그인
    login_data = {
        "email": user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/users/login", json=login_data)
    
    # Then
    assert response.status_code == 401
    assert "잘못된 이메일 또는 비밀번호" in response.json()["detail"]

def test_token_endpoint(client):
    """OAuth2 토큰 엔드포인트 테스트"""
    # Given - 사용자 생성
    user_data = {
        "email": "token_test@example.com",
        "username": "tokenuser",
        "password": "tokenpass123"
    }
    client.post("/api/users/", json=user_data)
    
    # When - 토큰 요청
    response = client.post(
        "/api/users/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Then
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_unauthorized_access(client):
    """인증되지 않은 요청이 보호된 엔드포인트 접근 시 401 반환 테스트"""
    # When - 인증 없이 보호된 엔드포인트 접근
    response = client.get("/api/users/")
    
    # Then
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()