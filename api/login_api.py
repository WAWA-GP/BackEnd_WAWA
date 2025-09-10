from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import Client as AsyncClient
from typing import Literal

from models.login_model import (UserCreate, UserUpdate, Token, SocialLoginUrl)
from db.login_supabase import get_supabase_client
from services import login_service

router = APIRouter()

# 클라이언트로부터 Bearer 토큰을 추출하기 위한 객체
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- API 엔드포인트 ---

@router.post("/register", status_code=201)
async def register(user: UserCreate, supabase: AsyncClient = Depends(get_supabase_client)):
    """
    ✅ 회원가입
    - Supabase Auth를 사용하여 새로운 사용자를 생성합니다.
    - is_admin 정보는 user_metadata에 저장됩니다.
    """
    return await login_service.register_user(user, supabase)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), supabase: AsyncClient = Depends(get_supabase_client)):
    """
    ✅ 로그인
    - 이메일(username 필드 사용)과 비밀번호로 로그인을 처리합니다.
    - 성공 시 Supabase가 생성한 JWT(access_token)를 반환합니다.
    """
    return await login_service.login_for_access_token(form_data, supabase)

@router.get("/login/{provider}", response_model=SocialLoginUrl)
async def social_login(provider: Literal["google", "kakao"], supabase: AsyncClient = Depends(get_supabase_client)):
    """
    ✅ 소셜 로그인 (구글, 카카오)
    - 지정된 provider의 로그인 페이지 URL을 생성하여 반환합니다.
    - 프론트엔드에서는 이 URL로 사용자를 리디렉션시켜야 합니다.
    """
    return await login_service.get_social_login_url(provider, supabase)

@router.get("/me")
async def protected_route(token: str = Depends(oauth2_scheme), supabase: AsyncClient = Depends(get_supabase_client)):
    """
    ✅ 보호된 라우트 (JWT 토큰 검증 예제)
    - 클라이언트가 제공한 토큰을 사용하여 사용자 정보를 가져옵니다.
    """
    return await login_service.get_current_user(token, supabase)


@router.put("/update")
async def update_user(
        user_update: UserUpdate,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    ✅ 사용자 정보 수정 (이메일, 비밀번호, is_admin)
    - 인증된 사용자만 자신의 정보를 수정할 수 있습니다.
    """
    return await login_service.update_user_info(user_update, token, supabase)
