from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User as DBUser
from app.utils.deps import get_current_user
from app.utils.exceptions import http_error, success_response
from app.utils.hash import hash_password  # 🔐 비밀번호 해시
from app.schemas import UserUpdate, UserResponse

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

# ✅ 사용자 정보 수정
@router.put("/update", response_model=UserResponse)
def update_user(
        updated_user: UserUpdate,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user)
):
    if updated_user.username:
        current_user.username = updated_user.username
    if updated_user.password:
        current_user.password = hash_password(updated_user.password)  # 🔐 비밀번호 해싱
    if updated_user.is_admin is not None:
        current_user.is_admin = updated_user.is_admin
    if updated_user.native_language:
        current_user.native_language = updated_user.native_language
    if updated_user.learning_language:
        current_user.learning_language = updated_user.learning_language
    if updated_user.level:
        current_user.level = updated_user.level

    db.commit()
    db.refresh(current_user)
    return current_user


# ✅ 프로필 조회
@router.get("/profile", response_model=UserResponse)
def get_profile(
        current_user: DBUser = Depends(get_current_user)
):
    return current_user