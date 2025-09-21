from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_admin, get_current_user
from models import notice_model
from services import notice_service

router = APIRouter(prefix="/notices")

@router.post("/", response_model=notice_model.NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(
        notice: notice_model.NoticeCreate,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    return notice_service.create_new_notice(db=db, notice_create=notice)

@router.get("/", response_model=List[notice_model.NoticeResponse])
def read_notices(
        skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return notice_service.get_all_notices(db=db, skip=skip, limit=limit)

@router.get("/{notice_id}", response_model=notice_model.NoticeResponse)
def read_notice(notice_id: int, db: Session = Depends(get_db)):
    db_notice = notice_service.get_notice_by_id(db=db, notice_id=notice_id)
    if db_notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    return db_notice

@router.put("/{notice_id}", response_model=notice_model.NoticeResponse)
def update_notice(
        notice_id: int,
        notice_update: notice_model.NoticeUpdate,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    updated_notice = notice_service.update_existing_notice(db=db, notice_id=notice_id, notice_update=notice_update)
    if updated_notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    return updated_notice

@router.delete("/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notice(
        notice_id: int,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    if not notice_service.delete_notice_by_id(db=db, notice_id=notice_id):
        raise HTTPException(status_code=404, detail="Notice not found")