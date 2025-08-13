from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User as DBUser
from app.schemas import UserCreate, UserUpdate
from app.utils.jwt_utils import create_access_token, decode_access_token
from app.utils.hash import hash_password, verify_password
from app.utils.deps import oauth2_scheme
from app.utils.exceptions import http_error

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
    return {"message": "회원가입 성공"}

# ✅ 로그인
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise http_error(401, "잘못된 사용자 이름 또는 비밀번호")

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ 보호된 라우트 (JWT 토큰 검증 예제)
@router.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise http_error(401, "토큰이 유효하지 않습니다")
    return {"message": f"{payload['sub']}님 인증 성공!"}

# ✅ 사용자 정보 수정 (비밀번호 포함)
@router.put("/update")
def update_user(
        user_update: UserUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
):
    payload = decode_access_token(token)
    if payload is None:
        raise http_error(401, "토큰이 유효하지 않습니다")

    username = payload.get("sub")
    db_user = db.query(DBUser).filter(DBUser.username == username).first()
    if not db_user:
        raise http_error(404, "사용자를 찾을 수 없습니다.")

    if user_update.username:
        db_user.username = user_update.username
    if user_update.password:
        db_user.password = hash_password(user_update.password)  # 🔐 비밀번호 변경 시 해싱
    if user_update.is_admin is not None:
        db_user.is_admin = user_update.is_admin

    db.commit()
    return {"message": "사용자 정보가 수정되었습니다."}