from fastapi import APIRouter, Depends, Header, HTTPException, Body, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import Client as AsyncClient
from typing import Literal, Any
from core import security
from pydantic import BaseModel

from core.database import get_db
from core.dependencies import get_current_user
from models.login_model import (UserCreate, UserUpdate, CharacterUpdate, LanguageSettingUpdate, UserProfileUpdate, TokenData, LoginResponse, SocialLoginUrl, UserLevelUpdate, UserProfileResponse,
                                NameCheckRequest, NameCheckResponse)
from db.login_supabase import get_supabase_client
from services import login_service
from models import user_model # user_model 임포트
from services import user_service # user_service 임포트

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

@router.patch("/update-details")
async def update_details(
        user_update: UserProfileUpdate,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client),
):
    """(인증 필요) 소셜 로그인 후 누락된 프로필 정보(이메일, 이름)를 업데이트합니다."""
    # 토큰에서 사용자 정보 가져오기
    user_response = await supabase.auth.get_user(token)
    user = user_response.user
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return await login_service.update_additional_user_info(str(user.id), user_update, supabase)

@router.get("/auth/{provider}/callback")
async def social_callback(
        provider: Literal["google", "kakao"],
        code: str,
        supabase: AsyncClient = Depends(get_supabase_client)
):
    """소셜 로그인 콜백을 처리합니다."""
    return await login_service.handle_social_callback(provider, code, supabase)

@router.patch("/update-languages")
async def update_languages(
        language_update: LanguageSettingUpdate,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client),
):
    """(인증 필요) 모국어와 학습 언어를 업데이트합니다."""
    user_response = await supabase.auth.get_user(token)
    user = user_response.user
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return await login_service.update_user_languages(
        str(user.id),
        language_update,
        supabase
    )

@router.patch("/update-character")
async def update_character(
        character_update: CharacterUpdate,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client),
):
    """(인증 필요) 선택한 캐릭터 정보를 업데이트합니다."""
    user_response = await supabase.auth.get_user(token)
    user = user_response.user
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return await login_service.update_user_character(
        str(user.id),
        character_update,
        supabase
    )

@router.post("/check-name")
async def check_name_availability(
        name: str = Body(..., embed=True),  # ✅ Body로 직접 받기
        supabase: AsyncClient = Depends(get_supabase_client)
):
    """이름 중복 검사 엔드포인트"""
    print(f"DEBUG: Received name: {name}")

    if not name or len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="이름은 2자 이상이어야 합니다.")

    is_available = await login_service.check_name_availability(name.strip(), supabase)
    return {"available": is_available}
