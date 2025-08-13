from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User as DBUser
from app.utils.jwt_utils import decode_access_token
from app.utils.deps import oauth2_scheme
from app.utils.exceptions import http_error
from app.utils.hash import hash_password  # 🔐 비밀번호 해시
from app.schemas import UserUpdate, UserProfileUpdate, UserProfileResponse

router = APIRouter()

# ✅ 사용자 정보 수정
@router.put("/user/update")
def update_user(
        updated_user: UserUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        raise http_error(401, "유효하지 않은 토큰입니다.")

    user = db.query(DBUser).filter(DBUser.username == payload["sub"]).first()
    if not user:
        raise http_error(404, "사용자를 찾을 수 없습니다.")

    if updated_user.username:
        user.username = updated_user.username
    if updated_user.password:
        user.password = hash_password(updated_user.password)  # 🔐 해싱
    if updated_user.is_admin is not None:
        user.is_admin = updated_user.is_admin

    db.commit()
    return {"message": "사용자 정보가 수정되었습니다."}

# ✅ 프로필 설정
@router.put("/user/profile")
def update_profile(
        profile_data: UserProfileUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        raise http_error(401, "유효하지 않은 토큰입니다.")

    user = db.query(DBUser).filter(DBUser.username == payload["sub"]).first()
    if not user:
        raise http_error(404, "사용자를 찾을 수 없습니다.")

    if profile_data.native_language:
        user.native_language = profile_data.native_language
    if profile_data.learning_language:
        user.learning_language = profile_data.learning_language
    if profile_data.learning_level:
        user.learning_level = profile_data.learning_level

    db.commit()
    return {"message": "프로필이 업데이트되었습니다."}

# ✅ 프로필 조회
@router.get("/user/profile", response_model=UserProfileResponse)
def get_profile(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        raise http_error(401, "유효하지 않은 토큰입니다.")

    user = db.query(DBUser).filter(DBUser.username == payload["sub"]).first()
    if not user:
        raise http_error(404, "사용자를 찾을 수 없습니다.")

    return user