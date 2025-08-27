from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, relationship

from app.database import get_db
from app.models import User as DBUser
from app.utils.deps import get_current_user
from app.utils.exceptions import http_error, success_response
from app.utils.hash import hash_password  # 🔐 비밀번호 해시
from app.schemas import UserUpdate, UserProfileUpdate, UserProfileResponse

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

# ✅ 사용자 정보 수정
@router.put("/update")
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

    db.commit()
    return success_response("사용자 정보가 수정되었습니다.")

# ✅ 프로필 설정
@router.put("/profile")
def update_profile(
        profile_data: UserProfileUpdate,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user)
):
    if profile_data.native_language:
        current_user.native_language = profile_data.native_language
    if profile_data.learning_language:
        current_user.learning_language = profile_data.learning_language
    if profile_data.learning_level:
        current_user.learning_level = profile_data.learning_level

    db.commit()
    return success_response("프로필이 업데이트되었습니다.")

# ✅ 프로필 조회
@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
        current_user: DBUser = Depends(get_current_user)
):
    return success_response("프로필 조회 성공", data=current_user)

# 출석체크
# User 모델 안에
attendances = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")