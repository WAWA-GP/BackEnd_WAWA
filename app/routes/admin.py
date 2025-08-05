from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.utils.deps import get_current_admin
from app.database import SessionLocal
from app.models import (
    User,
    Notice, NoticeCreate, NoticeResponse,
    FAQ, FAQCreate, FAQResponse,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ 관리자 대시보드
@router.get("/dashboard")
def admin_dashboard(current_admin: User = Depends(get_current_admin)):
    return {
        "message": f"관리자 {current_admin.username}님 환영합니다!",
        "admin": True
    }

# ✅ 공지사항 생성
@router.post("/notices", response_model=NoticeResponse)
def create_notice(
        notice: NoticeCreate,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    new_notice = Notice(**notice.dict())
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return new_notice

# ✅ 공지사항 전체 조회
@router.get("/notices", response_model=List[NoticeResponse])
def list_notices(
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    return db.query(Notice).all()

# ✅ FAQ 생성
@router.post("/faqs", response_model=FAQResponse)
def create_faq(
        faq: FAQCreate,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    new_faq = FAQ(**faq.dict())
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq

# ✅ FAQ 전체 조회
@router.get("/faqs", response_model=List[FAQResponse])
def list_faqs(
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    return db.query(FAQ).all()
