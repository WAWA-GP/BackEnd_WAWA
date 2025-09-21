# 'Notice' 모델에 대한 데이터베이스 CRUD 작업을 정의하는 파일입니다.
from sqlalchemy.orm import Session
from database import models as db_models
from models import notice_model

# --- 특정 공지사항 조회 ---
def get_notice(db: Session, notice_id: int):
    return db.query(db_models.Notice).filter(db_models.Notice.id == notice_id).first()

# --- 모든 공지사항 조회 (페이지네이션) ---
def get_notices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_models.Notice).order_by(db_models.Notice.id.desc()).offset(skip).limit(limit).all()

# --- 공지사항 생성 ---
def create_notice(db: Session, notice: notice_model.NoticeCreate):
    db_notice = db_models.Notice(**notice.dict())
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice

# --- 공지사항 수정 ---
def update_notice(db: Session, notice_id: int, update_data: dict):
    db_notice = get_notice(db, notice_id)
    if not db_notice:
        return None
    for key, value in update_data.items():
        setattr(db_notice, key, value)
    db.commit()
    db.refresh(db_notice)
    return db_notice

# --- 공지사항 삭제 ---
def delete_notice(db: Session, notice_id: int):
    db_notice = get_notice(db, notice_id)
    if not db_notice:
        return False
    db.delete(db_notice)
    db.commit()
    return True