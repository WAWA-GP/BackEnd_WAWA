from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User as DBUser, UserUpdate
from app.utils.jwt_utils import decode_access_token
from app.utils.deps import oauth2_scheme  # ✅ 여기서 가져와야 함
from app.utils.exceptions import http_error

router = APIRouter()

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
        user.password = updated_user.password  # 🔐 실제 서비스에선 해싱 필요
    if updated_user.is_admin is not None:
        user.is_admin = updated_user.is_admin

    db.commit()
    return {"message": "사용자 정보가 수정되었습니다."}
