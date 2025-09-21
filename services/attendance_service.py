# '출석 체크' 관련 비즈니스 로직을 처리하는 파일입니다.
from sqlalchemy.orm import Session
from db import attendance_crud
from datetime import date, timedelta

# --- 출석 체크 서비스 ---
def mark_attendance(db: Session, user_id: int):
    today = date.today()
    existing = attendance_crud.get_attendance_by_date(db, user_id=user_id, date=today)
    if existing:
        return None
    return attendance_crud.create_attendance(db, user_id=user_id, date=today)

# --- 전체 출석 기록 조회 서비스 ---
def get_user_attendance_history(db: Session, user_id: int):
    return attendance_crud.get_all_attendances_by_user(db, user_id=user_id)

# --- 출석 통계 계산 서비스 ---
def calculate_stats(db: Session, user_id: int):
    records = attendance_crud.get_all_attendances_by_user(db, user_id=user_id)
    if not records:
        return {"total_days": 0, "longest_streak": 0}

    total_days = len(records)

    streak = 0
    max_streak = 0

    sorted_dates = sorted([r.date for r in records])

    if sorted_dates:
        streak = 1
        max_streak = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i-1] + timedelta(days=1):
                streak += 1
            else:
                streak = 1
            max_streak = max(max_streak, streak)

    return {"total_days": total_days, "longest_streak": max_streak}