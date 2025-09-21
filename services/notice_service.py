# '공지사항' 관련 비즈니스 로직을 처리하는 파일입니다.
from sqlalchemy.orm import Session
from models import notice_model
from db import notice_crud

# --- 새 공지사항 생성 서비스 ---
def create_new_notice(db: Session, notice_create: notice_model.NoticeCreate):
    return notice_crud.create_notice(db=db, notice=notice_create)

# --- 모든 공지사항 조회 서비스 ---
def get_all_notices(db: Session, skip: int = 0, limit: int = 100):
    return notice_crud.get_notices(db=db, skip=skip, limit=limit)

# --- 특정 공지사항 조회 서비스 ---
def get_notice_by_id(db: Session, notice_id: int):
    return notice_crud.get_notice(db=db, notice_id=notice_id)

# --- 공지사항 수정 서비스 ---
def update_existing_notice(db: Session, notice_id: int, notice_update: notice_model.NoticeUpdate):
    update_data = notice_update.dict(exclude_unset=True)
    return notice_crud.update_notice(db=db, notice_id=notice_id, update_data=update_data)

# --- 공지사항 삭제 서비스 ---
def delete_notice_by_id(db: Session, notice_id: int):
    return notice_crud.delete_notice(db=db, notice_id=notice_id)