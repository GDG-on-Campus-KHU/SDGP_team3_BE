from datetime import datetime

# for fake user
from app.database.fake_data import get_fake_user_info
from app.models.user_model import User, UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

# class GoogleAuthService:
#     @staticmethod
#     async def login_or_register(user_info: dict) -> str:
#         email = user_info["email"]
#         username = user_info.get("name", "google_user")

#         user = await UserRepository.get_user_by_email(email)
#         # DB에 존재하지 않는 사용자일 경우
#         if not user:
#             user = await UserRepository.create_user(UserCreate(
#                 email = email,
#                 username = username,
#                 password = "placeholder_PW_google"
#             ))
#         return UserService.create_access_token(data={"sub":user.id})


class GoogleAuthService:
    # @staticmethod
    # async def login_or_register(user_info: dict) -> str:
    #     # 실제 DB 연동은 생략하고, 가짜 유저 객체 생성
    #     fake_user = get_fake_user_info(user_info)

    #     token = UserService.create_access_token(data={"sub": str(fake_user.id)})
    #     return token

    @staticmethod
    async def login_or_register(user_info: dict) -> str:
        email = user_info["email"]
        username = user_info.get("name", "google_user")

        user = await UserRepository.get_user_by_email(email)

        if not user:
            user = await UserRepository.create_user(
                UserCreate(
                    email=email,
                    username=username,
                    password="placeholder_google_oauth"
                )
            )
            if not user : 
                raise Exception("유저 생성 실패")

        return UserService.create_access_token(data={"sub": str(user.email)})
    
    @staticmethod
    async def get_or_create_user(email: str, username: str) -> User:
        user = await UserRepository.get_user_by_email(email)

        if not user:
            user = await UserRepository.create_user(
                UserCreate(
                    email=email,
                    username=username,
                    password="placeholder_google_oauth"
                )
            )
            if not user:
                raise Exception("유저 생성 실패")

        return user