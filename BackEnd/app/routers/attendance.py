from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models import Attendance, User
from app.utils.deps import get_current_user
from app.utils.exceptions import http_error

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

# ✅ 1. 출석 체크하기
@router.post("/check")
def check_attendance(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    today = date.today()
    existing = (
        db.query(Attendance)
        .filter(Attendance.user_id == current_user.id, Attendance.date == today)
        .first()
    )

    if existing:
        return {"message": "이미 오늘 출석체크 완료"}

    new_record = Attendance(user_id=current_user.id, date=today)
    db.add(new_record)
    db.commit()
    return {"message": "출석체크 성공!"}


# ✅ 2. 출석 기록 조회
@router.get("/history")
def get_attendance_history(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    records = (
        db.query(Attendance)
        .filter(Attendance.user_id == current_user.id)
        .order_by(Attendance.date.desc())
        .all()
    )
    return {"attendance_history": [{"date": r.date, "created_at": r.created_at} for r in records]}


# ✅ 3. 출석 통계 (총 출석일, 최근 연속 출석일)
@router.get("/stats")
def get_attendance_stats(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    records = (
        db.query(Attendance)
        .filter(Attendance.user_id == current_user.id)
        .order_by(Attendance.date.asc())
        .all()
    )

    total_days = len(records)
    streak = 0
    max_streak = 0
    prev_day = None

    for r in records:
        if prev_day and (r.date - prev_day).days == 1:
            streak += 1
        else:
            streak = 1
        max_streak = max(max_streak, streak)
        prev_day = r.date

    return {
        "total_days": total_days,
        "longest_streak": max_streak,
        "last_checked": records[-1].date if records else None
    }