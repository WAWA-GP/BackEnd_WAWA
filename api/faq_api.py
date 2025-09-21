# 'FAQ' 관련 API 엔드포인트를 정의하는 파일입니다.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_admin
from models import faq_model
from services import faq_service

router = APIRouter(prefix="/faqs")

# --- FAQ 생성 API ---
@router.post("/", response_model=faq_model.FAQResponse, status_code=status.HTTP_201_CREATED)
def create_faq(
        faq: faq_model.FAQCreate,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    return faq_service.create_new_faq(db=db, faq_create=faq)

# --- FAQ 목록 조회 API ---
@router.get("/", response_model=List[faq_model.FAQResponse])
def read_faqs(
        skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return faq_service.get_all_faqs(db=db, skip=skip, limit=limit)

# --- 특정 FAQ 조회 API ---
@router.get("/{faq_id}", response_model=faq_model.FAQResponse)
def read_faq(faq_id: int, db: Session = Depends(get_db)):
    db_faq = faq_service.get_faq_by_id(db=db, faq_id=faq_id)
    if db_faq is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return db_faq

# --- FAQ 수정 API ---
@router.put("/{faq_id}", response_model=faq_model.FAQResponse)
def update_faq(
        faq_id: int,
        faq_update: faq_model.FAQUpdate,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    updated_faq = faq_service.update_existing_faq(db=db, faq_id=faq_id, faq_update=faq_update)
    if updated_faq is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return updated_faq

# --- FAQ 삭제 API ---
@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(
        faq_id: int,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    if not faq_service.delete_faq_by_id(db=db, faq_id=faq_id):
        raise HTTPException(status_code=404, detail="FAQ not found")