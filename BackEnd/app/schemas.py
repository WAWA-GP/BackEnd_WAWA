from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

# -------------------------------
# ✅ 사용자 관련 스키마
# -------------------------------

# 사용자 생성 요청
class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: Optional[bool] = False


# 사용자 정보 수정 요청 (프로필 포함)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    native_language: Optional[str] = None
    learning_language: Optional[str] = None
    level: Optional[str] = None   # beginner / intermediate / advanced


# 사용자 응답
class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_active: bool
    native_language: Optional[str] = None
    learning_language: Optional[str] = None
    level: str

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


# 공지사항 목록 페이징 응답
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


# FAQ 목록 페이징 응답
class FAQListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FAQResponse]


# -------------------------------
# ✅ 레벨 테스트 관련 스키마
# -------------------------------

# 문제 생성 요청
class LevelTestQuestionCreate(BaseModel):
    question_text: str
    correct_answer: str
    difficulty: int   # 1=초급, 2=중급, 3=고급


# 문제 응답
class LevelTestQuestionResponse(BaseModel):
    id: int
    question_text: str
    difficulty: int

    class Config:
        orm_mode = True


# 사용자 풀이 요청
class LevelTestSubmit(BaseModel):
    answers: List[str]   # 제출 답안 리스트


# 결과 응답
class LevelTestResultResponse(BaseModel):
    id: int
    user_id: int
    score: int
    level: str   # beginner / intermediate / advanced

    class Config:
        orm_mode = True


# -------------------------------
# ✅ 출석체크 관련 스키마
# -------------------------------

# 출석 응답
class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    date: date
    created_at: datetime

    class Config:
        orm_mode = True


# 출석 목록 응답
class AttendanceListResponse(BaseModel):
    total: int
    items: List[AttendanceResponse]