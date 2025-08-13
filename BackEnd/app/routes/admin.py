from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.utils.deps import get_current_admin
from app.database import SessionLocal
from app.models import User, Notice, FAQ
from app.schemas import (
    NoticeCreate, NoticeUpdate, NoticeResponse,
    FAQCreate, FAQUpdate, FAQResponse
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# ✅ DB 세션 의존성
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

# ============================
# ✅ 공지사항 기능
# ============================

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

@router.get("/notices", response_model=List[NoticeResponse])
def list_notices(
        keyword: Optional[str] = Query(None),
        limit: int = Query(10, ge=1),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    query = db.query(Notice)
    if keyword:
        query = query.filter(
            or_(
                Notice.title.contains(keyword),
                Notice.content.contains(keyword)
            )
        )
    return query.order_by(Notice.id.desc()).offset(offset).limit(limit).all()

@router.get("/notices/{notice_id}", response_model=NoticeResponse)
def get_notice(
        notice_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")
    return notice

@router.put("/notices/{notice_id}")
def update_notice(
        notice_id: int,
        notice_update: NoticeUpdate,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")

    if notice_update.title is not None:
        notice.title = notice_update.title
    if notice_update.content is not None:
        notice.content = notice_update.content

    db.commit()
    return {"message": "공지사항이 수정되었습니다."}

@router.delete("/notices/{notice_id}")
def delete_notice(
        notice_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다.")

    db.delete(notice)
    db.commit()
    return {"message": "공지사항이 삭제되었습니다."}

# ============================
# ✅ FAQ 기능
# ============================

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

@router.get("/faqs", response_model=List[FAQResponse])
def list_faqs(
        keyword: Optional[str] = Query(None),
        limit: int = Query(10, ge=1),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    query = db.query(FAQ)
    if keyword:
        query = query.filter(
            or_(
                FAQ.question.contains(keyword),
                FAQ.answer.contains(keyword)
            )
        )
    return query.order_by(FAQ.id.desc()).offset(offset).limit(limit).all()

@router.get("/faqs/{faq_id}", response_model=FAQResponse)
def get_faq(
        faq_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ를 찾을 수 없습니다.")
    return faq

@router.put("/faqs/{faq_id}")
def update_faq(
        faq_id: int,
        faq_update: FAQUpdate,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ를 찾을 수 없습니다.")

    if faq_update.question is not None:
        faq.question = faq_update.question
    if faq_update.answer is not None:
        faq.answer = faq_update.answer

    db.commit()
    return {"message": "FAQ가 수정되었습니다."}

@router.delete("/faqs/{faq_id}")
def delete_faq(
        faq_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ를 찾을 수 없습니다.")

    db.delete(faq)
    db.commit()
    return {"message": "FAQ가 삭제되었습니다."}