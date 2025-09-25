from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import Client as AsyncClient
from typing import Literal

# ▼▼▼ [수정] Token 대신 LoginResponse와 UserProfileResponse를 import 합니다. ▼▼▼
from models.login_model import (UserCreate, UserUpdate, TokenData, LoginResponse, SocialLoginUrl, UserLevelUpdate, UserProfileResponse)
from db.login_supabase import get_supabase_client
from services import login_service

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", status_code=201)
async def register(user: UserCreate, supabase: AsyncClient = Depends(get_supabase_client)):
    # 👇 [수정] 이제 이 함수는 토큰과 유저 정보를 반환합니다.
    return await login_service.register_user(user, supabase)

@router.post("/create-profile", status_code=201)
async def create_profile_endpoint(
        authorization: str = Header(...), # 헤더에서 토큰을 받음
        supabase: AsyncClient = Depends(get_supabase_client)
):
    token = authorization.split(" ")[1]
    return await login_service.create_user_profile(token, supabase)

@router.get("/profile", response_model=UserProfileResponse)
async def get_my_profile(
        authorization: str = Header(None), # None을 기본값으로 하여 헤더가 없을 수도 있음을 명시
        supabase: AsyncClient = Depends(get_supabase_client)
):
    # 👇 [수정] 토큰을 안전하게 파싱하는 로직으로 변경
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="인증 헤더가 없거나 형식이 잘못되었습니다."
        )

    token_parts = authorization.split(" ")
    if len(token_parts) != 2:
        raise HTTPException(
            status_code=401,
            detail="인증 토큰 형식이 잘못되었습니다."
        )

    token = token_parts[1]
    # --- [수정된 부분 끝] ---

    return await login_service.get_current_user(token=token, supabase=supabase)

# ▼▼▼ [수정] response_model을 통합된 LoginResponse로 변경합니다. ▼▼▼
@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), supabase: AsyncClient = Depends(get_supabase_client)):
    return await login_service.login_for_access_token(form_data, supabase)

@router.get("/login/{provider}", response_model=SocialLoginUrl)
async def social_login(provider: Literal["google", "kakao"], supabase: AsyncClient = Depends(get_supabase_client)):
    return await login_service.get_social_login_url(provider, supabase)

@router.put("/update")
async def update_user(
        user_update: UserUpdate,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client),
):
    return await login_service.update_user_info(user_update, token, supabase)

@router.post("/update-level")
async def update_level(level_update: UserLevelUpdate, supabase: AsyncClient = Depends(get_supabase_client)):
    return await login_service.update_user_assessed_level(
        email=level_update.email,
        level=level_update.assessed_level,
        supabase=supabase
    )

@router.post("/login/auto")
async def auto_login(token_data: TokenData, supabase: AsyncClient = Depends(get_supabase_client)):
    return await login_service.auto_login_with_token(token_data.token, supabase)
