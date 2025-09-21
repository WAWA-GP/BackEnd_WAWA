# 'FAQ' 관련 비즈니스 로직을 처리하는 파일입니다.
from sqlalchemy.orm import Session
from models import faq_model
from db import faq_crud

# --- 새 FAQ 생성 서비스 ---
def create_new_faq(db: Session, faq_create: faq_model.FAQCreate):
    return faq_crud.create_faq(db=db, faq=faq_create)

# --- 모든 FAQ 조회 서비스 ---
def get_all_faqs(db: Session, skip: int = 0, limit: int = 100):
    return faq_crud.get_faqs(db=db, skip=skip, limit=limit)

# --- 특정 FAQ 조회 서비스 ---
def get_faq_by_id(db: Session, faq_id: int):
    return faq_crud.get_faq(db=db, faq_id=faq_id)

# --- FAQ 수정 서비스 ---
def update_existing_faq(db: Session, faq_id: int, faq_update: faq_model.FAQUpdate):
    update_data = faq_update.dict(exclude_unset=True)
    return faq_crud.update_faq(db=db, faq_id=faq_id, update_data=update_data)

# --- FAQ 삭제 서비스 ---
def delete_faq_by_id(db: Session, faq_id: int):
    return faq_crud.delete_faq(db=db, faq_id=faq_id)