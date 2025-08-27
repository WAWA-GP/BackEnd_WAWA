from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User as DBUser
from app.schemas import UserCreate, UserUpdate
from app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)
from app.utils.hash import hash_password, verify_password
from app.utils.deps import get_current_user
from app.utils.exceptions import http_error, success_response

# ✅ 현재 로그인 세션 관리용 (중복 로그인 방지)
active_sessions = {}

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


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
    db.commit()

    return success_response("회원가입 성공")


# ✅ 로그인 (중복 로그인 방지 + Refresh Token 발급)
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise http_error(401, "잘못된 사용자 이름 또는 비밀번호")

    if user.username in active_sessions:
        raise http_error(409, "이미 다른 기기에서 로그인 중입니다.")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    active_sessions[user.username] = access_token

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
    username = current_user.username
    if username in active_sessions:
        del active_sessions[username]
    return success_response("로그아웃 성공")


# ✅ 보호된 라우트 (JWT 토큰 검증 예제)
@router.get("/protected")
def protected_route(current_user: DBUser = Depends(get_current_user)):
    return success_response(f"{current_user.username}님 인증 성공!")


# ✅ 사용자 정보 수정
@router.put("/update")
def update_user(
        user_update: UserUpdate,
        current_user: DBUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    if user_update.username:
        current_user.username = user_update.username
    if user_update.password:
        current_user.password = hash_password(user_update.password)
    if user_update.is_admin is not None:
        current_user.is_admin = user_update.is_admin
    if user_update.native_language:
        current_user.native_language = user_update.native_language
    if user_update.target_language:
        current_user.target_language = user_update.target_language

    db.commit()
    return success_response("사용자 정보가 수정되었습니다.")

# ✅ 회원 탈퇴 (논리 삭제)
@router.delete("/delete")
def delete_user(
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    if not current_user.is_active:
        return {"message": "이미 탈퇴 처리된 사용자입니다."}

    current_user.is_active = False
    db.commit()
    return {"message": "회원탈퇴 처리되었습니다. (데이터는 보관됨)"}