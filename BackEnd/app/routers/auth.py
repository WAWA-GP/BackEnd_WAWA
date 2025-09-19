from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User as DBUser
from app.schemas import UserCreate
from app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)
from app.utils.hash import hash_password, verify_password
from app.utils.deps import get_current_user
from app.utils.exceptions import http_error, success_response
from pydantic import BaseModel

# ✅ 현재 로그인 세션 관리용 (중복 로그인 방지)
active_sessions = {}

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# ✅ JSON 로그인 요청용 스키마
class UserLogin(BaseModel):
    username: str
    password: str


# ✅ 회원가입
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if existing_user:
        raise http_error(400, "이미 존재하는 사용자입니다.")

    hashed_pw = hash_password(user.password)
    new_user = DBUser(
        username=user.username,
        password=hashed_pw,
        is_admin=user.is_admin or False
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise http_error(400, "이미 존재하는 사용자입니다.")

    return {"message": "회원가입 성공", "username": new_user.username}


# ✅ 로그인 (JSON 요청 지원)
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise http_error(401, "잘못된 사용자 이름 또는 비밀번호")

    if db_user.username in active_sessions:
        raise http_error(409, "이미 다른 기기에서 로그인 중입니다.")

    access_token = create_access_token({"sub": db_user.username})
    refresh_token = create_refresh_token({"sub": db_user.username})

    active_sessions[db_user.username] = access_token

    return success_response(
        "로그인 성공",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    )


# ✅ Refresh Token → 새로운 Access Token 재발급
@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise http_error(401, "유효하지 않은 Refresh Token입니다.")

    user = db.query(DBUser).filter(DBUser.username == payload["sub"]).first()
    if not user:
        raise http_error(404, "사용자를 찾을 수 없습니다.")

    new_access_token = create_access_token({"sub": user.username})
    active_sessions[user.username] = new_access_token

    return success_response(
        "Access Token 재발급 성공",
        data={"access_token": new_access_token, "token_type": "bearer"}
    )


# ✅ 로그아웃
@router.post("/logout")
def logout(current_user: DBUser = Depends(get_current_user)):
    if not current_user:
        raise http_error(401, "로그인 상태가 아닙니다.")

    username = current_user.username
    if username in active_sessions:
        del active_sessions[username]

    return success_response("로그아웃 성공")


# ✅ 보호된 라우트 (JWT 토큰 검증 예제)
@router.get("/protected")
def protected_route(current_user: DBUser = Depends(get_current_user)):
    return success_response(f"{current_user.username}님 인증 성공!")