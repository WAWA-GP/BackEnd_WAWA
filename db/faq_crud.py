# 'FAQ' 모델에 대한 데이터베이스 CRUD 작업을 정의하는 파일입니다.
from sqlalchemy.orm import Session
from database import models as db_models
from models import faq_model

# --- 특정 FAQ 조회 ---
def get_faq(db: Session, faq_id: int):
    return db.query(db_models.FAQ).filter(db_models.FAQ.id == faq_id).first()

# --- 모든 FAQ 조회 (페이지네이션) ---
def get_faqs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_models.FAQ).order_by(db_models.FAQ.id.desc()).offset(skip).limit(limit).all()

# --- FAQ 생성 ---
def create_faq(db: Session, faq: faq_model.FAQCreate):
    db_faq = db_models.FAQ(**faq.dict())
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

# --- FAQ 수정 ---
def update_faq(db: Session, faq_id: int, update_data: dict):
    db_faq = get_faq(db, faq_id)
    if not db_faq:
        return None
    for key, value in update_data.items():
        setattr(db_faq, key, value)
    db.commit()
    db.refresh(db_faq)
    return db_faq

# --- FAQ 삭제 ---
def delete_faq(db: Session, faq_id: int):
    db_faq = get_faq(db, faq_id)
    if not db_faq:
        return False
    db.delete(db_faq)
    db.commit()
    return True