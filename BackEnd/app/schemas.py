from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# -------------------------------
# ✅ 사용자 관련 스키마
# -------------------------------

# 사용자 생성 요청
class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: Optional[bool] = False

# 사용자 정보 수정 요청
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

# 사용자 프로필 설정 요청
class UserProfileUpdate(BaseModel):
    native_language: Optional[str] = None
    learning_language: Optional[str] = None
    learning_level: Optional[str] = None

# 사용자 프로필 응답
class UserProfileResponse(BaseModel):
    username: str
    native_language: Optional[str] = None
    learning_language: Optional[str] = None
    learning_level: Optional[str] = None

    class Config:
        orm_mode = True

# -------------------------------
# ✅ 공지사항 관련 스키마
# -------------------------------

# 공지사항 생성 요청
class NoticeCreate(BaseModel):
    title: str
    content: str

# 공지사항 수정 요청
class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# 공지사항 응답
class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

# ✅ 공지사항 목록 페이징 응답
class NoticeListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[NoticeResponse]

# -------------------------------
# ✅ FAQ 관련 스키마
# -------------------------------

# FAQ 생성 요청
class FAQCreate(BaseModel):
    question: str
    answer: str

# FAQ 수정 요청
class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

# FAQ 응답
class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True

# ✅ FAQ 목록 페이징 응답
class FAQListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FAQResponse]