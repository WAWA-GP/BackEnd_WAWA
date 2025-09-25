from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Dict


# Pydantic V2에서는 Union 타입을 | (파이프)로 표현하는 것을 권장합니다.
# from typing import Union -> Optional[str] 또는 str | None 으로 대체

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    is_admin: bool = False

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

# ▼▼▼ [수정] Token과 LoginResponse를 하나로 통합합니다. ▼▼▼
class LoginResponse(BaseModel):
    """로그인 성공 시 반환하는 통합 데이터 모델"""
    access_token: str
    token_type: str
    assessed_level: Optional[str] = None
    is_admin: Optional[bool] = None

class SocialLoginUrl(BaseModel):
    url: str

class UserLevelUpdate(BaseModel):
    email: str
    assessed_level: str

class TokenData(BaseModel):
    token: str

class UserProfileResponse(BaseModel):
    """API가 반환하는 사용자 프로필 정보 모델"""
    user_id: str
    email: EmailStr
    name: str
    assessed_level: Optional[str] = None
    # 👈 [수정] learning_goals 필드를 추가하고, created_at은 선택사항으로 변경합니다.
    learning_goals: Optional[Dict] = None
    created_at: Optional[str] = None
    is_admin: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
