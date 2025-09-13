from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.utils.jwt_utils import decode_access_token
from app.models import User
from app.database import SessionLocal
from app.utils.exceptions import http_error

# ✅ OAuth2 스킴 (토큰 발급 경로 지정)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ✅ DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ 현재 로그인한 사용자 반환 (is_active 필터링 포함)
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise http_error(401, "토큰이 유효하지 않습니다")

    user = (
        db.query(User)
        .filter(User.username == payload["sub"], User.is_active == True)
        .first()
    )
    if not user:
        raise http_error(401, "유효하지 않거나 탈퇴한 사용자입니다")

    return user


# ✅ 현재 로그인한 사용자가 관리자 권한인지 확인
def get_current_admin(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    user = get_current_user(token, db)
    if not user.is_admin:
        raise http_error(403, "관리자 권한이 필요합니다")

    return user