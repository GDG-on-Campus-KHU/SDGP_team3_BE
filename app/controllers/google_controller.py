import secrets
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import RedirectResponse

from app.core.oauth import oauth
from app.services.google_service import GoogleAuthService

router = APIRouter(prefix="/api/google", tags=["Google Auth"])
# localhost:8000/api/google


@router.get("/login")
async def google_login(request: Request) -> Any:
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)

    request.session["state"] = state
    request.session["nonce"] = nonce

    # state를 세션에 저장
    print("저장된 state:", state)

    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(
        request, redirect_uri, state=state, nonce=nonce
    )


@router.get("/callback")
async def google_callback(request: Request) -> Dict[str, Any]:
    session_state = request.session.get("state")
    session_nonce = request.session.get("nonce")

    if not session_state or session_state != request.query_params.get("state"):
        raise HTTPException(status_code=400, detail="CSRF Warning! State mismatch.")
    # 디버깅용
    # print("받은 state:", state)
    print("세션 state:", request.session.get("state"))
    print("쿼리파라미터 state:", request.query_params.get("state"))

    token = await oauth.google.authorize_access_token(
        request
    )  # 구글이 준 인증코드로 토큰 요청
    print("받은 token:", token)

    if not token or "id_token" not in token:
        raise HTTPException(
            status_code=400, detail="Google에서 id_token을 반환하지 않았습니다."
        )

    # claims = await oauth.google.parse_id_token(token=token, request=request, nonce=session_nonce)
    # print("받은 claims:", claims)

    # user_info = {
    #     "email": claims.get("email"),
    #     "name": claims.get("name"),
    #     "picture": claims.get("picture"),
    #     "sub": claims.get("sub")
    # }
    user_info = await oauth.google.userinfo(token=token)
    print("user_info:", user_info)

    jwt_token = await GoogleAuthService.login_or_register(
        {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "sub": user_info.get("sub"),
        }
    )

    return {"access_token": jwt_token, "token_type": "bearer"}
