# '사용자' 기능과 관련된 데이터 형식을 Pydantic 모델로 정의하는 파일입니다.
from pydantic import BaseModel
from typing import Optional

# --- 사용자 생성을 위한 요청 스키마 ---
# API를 통해 사용자를 생성할 때 받아들일 필드를 정의합니다.
class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

# --- 사용자 정보 수정을 위한 요청 스키마 ---
# 모든 필드가 Optional이므로, 클라이언트는 수정하고 싶은 필드만 요청에 포함할 수 있습니다.
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    native_language: Optional[str] = None
    learning_language: Optional[str] = None

# --- API 응답에 사용될 사용자 정보 스키마 ---
# 클라이언트에게 반환할 사용자 정보의 구조를 정의합니다.
# password 필드가 없으므로, API 응답에 절대 포함되지 않습니다.
class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_active: bool
    native_language: Optional[str] = None
    learning_language: Optional[str] = None
    level: str

    class Config:
        # orm_mode=True 설정은 SQLAlchemy ORM 객체를 이 Pydantic 모델로 자동으로 변환할 수 있게 해줍니다.
        orm_mode = True
