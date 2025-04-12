from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from app.core.oauth import oauth
from app.services.google_service import GoogleAuthService
import secrets

router = APIRouter(prefix="/api/google", tags=["Google Auth"])
# localhost:8000/api/google

@router.get("/login")
async def google_login(request : Request):
    state = secrets.token_urlsafe(16)
    request.session["state"] = state
    # state를 세션에 저장
    print("저장된 state:", state)

    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)

@router.get("/callback")
async def google_callback(request: Request):
    state = request.session.get("state")
    if not state or state != request.query_params.get("state"):
        raise HTTPException(status_code=400, detail="CSRF Warning! State mismatch.")
    # 디버깅용
    print("받은 state:", state)

    token = await oauth.google.authorize_access_token(request) # 구글이 준 인증코드로 토큰 요청
    print("받은 token:" , token)

    if not token or "id_token" not in token:
        raise HTTPException(status_code=400, detail="Google에서 id_token을 반환하지 않았습니다.")

    claims = await oauth.google.parse_id_token(token, request)
    print("받은 claims:", claims)

    user_info = {
        "email": claims.get("email"),
        "name": claims.get("name"),
        "picture": claims.get("picture"),
        "sub": claims.get("sub")
    }

    jwt_token = await GoogleAuthService.login_or_register(user_info)
    return {"access_token": jwt_token}