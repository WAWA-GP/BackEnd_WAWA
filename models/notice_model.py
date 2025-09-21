# '공지사항' 관련 데이터 형식을 Pydantic 모델로 정의합니다.
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- 공지사항의 기본 필드를 정의하는 기본 모델 ---
class NoticeBase(BaseModel):
    title: str
    content: str

# --- 공지사항 생성을 위한 요청 스키마 ---
class NoticeCreate(NoticeBase):
    pass

# --- 공지사항 수정을 위한 요청 스키마 ---
class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# --- 공지사항 API 응답 스키마 ---
class NoticeResponse(NoticeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True