# API 엔드포인트에서 공통으로 사용될 의존성 함수들을 정의합니다.
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette import status

from core.database import get_db
from core import security
from db import user_crud
from database import models as db_models

# 'Authorization: Bearer <token>' 헤더에서 토큰을 추출하는 보안 스키마입니다.
bearer_scheme = HTTPBearer()

# 현재 요청의 토큰을 검증하고, 유효하다면 해당 사용자 정보를 반환하는 의존성 함수입니다.
def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)
) -> db_models.User:
    username = security.get_username_from_token(token.credentials)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = user_crud.get_user_by_username(db, username=username)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user

# 현재 로그인한 사용자가 관리자인지 확인하는 의존성 함수입니다.
def get_current_admin(current_user: db_models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user