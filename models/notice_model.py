<<<<<<< HEAD
=======
# '공지사항' 관련 데이터 형식을 Pydantic 모델로 정의합니다.
>>>>>>> origin/master
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

<<<<<<< HEAD
=======
# --- 공지사항의 기본 필드를 정의하는 기본 모델 ---
>>>>>>> origin/master
class NoticeBase(BaseModel):
    title: str
    content: str

<<<<<<< HEAD
class NoticeCreate(NoticeBase):
    pass

=======
# --- 공지사항 생성을 위한 요청 스키마 ---
class NoticeCreate(NoticeBase):
    pass

# --- 공지사항 수정을 위한 요청 스키마 ---
>>>>>>> origin/master
class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

<<<<<<< HEAD
=======
# --- 공지사항 API 응답 스키마 ---
>>>>>>> origin/master
class NoticeResponse(NoticeBase):
    id: int
    created_at: datetime

    class Config:
<<<<<<< HEAD
        from_attributes = True
=======
        orm_mode = True
>>>>>>> origin/master
