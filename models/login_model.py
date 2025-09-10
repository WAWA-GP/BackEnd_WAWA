from pydantic import BaseModel, EmailStr
from typing import Literal

# 회원 가입 요청
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

# 사용자 정보 수정
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_admin: bool | None = None

# 로그인 성공 시 JWT 토큰 반환
class Token(BaseModel):
    """로그인 성공 시 반환하는 JWT 토큰 모델"""
    access_token: str
    token_type: str

# 소셜 로그인 URL 반환
class SocialLoginUrl(BaseModel):
    url: str
