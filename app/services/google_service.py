from app.models.user_model import UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

class GoogleAuthService:
    @staticmethod
    async def login_or_register(user_info: dict) -> str:
        email = user_info["email"]
        username = user_info.get("name", "google_user")

        user = await UserRepository.get_user_by_email(email)
        # DB에 존재하지 않는 사용자일 경우
        if not user:
            user = await UserRepository.create_user(UserCreate(
                email = email,
                username = username,
                password = "placeholder_PW_google"
            ))
        return UserService.create_access_token(data={"sub":user.id})