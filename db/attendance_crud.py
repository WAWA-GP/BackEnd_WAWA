# 'Attendance' 모델에 대한 데이터베이스 CRUD 작업을 정의하는 파일입니다.
from sqlalchemy.orm import Session
from database import models as db_models
from datetime import date

# --- 특정 날짜의 출석 기록 조회 ---
def get_attendance_by_date(db: Session, user_id: int, date: date):
    return db.query(db_models.Attendance).filter(
        db_models.Attendance.user_id == user_id,
        db_models.Attendance.date == date
    ).first()

# --- 출석 기록 생성 ---
def create_attendance(db: Session, user_id: int, date: date):
    db_attendance = db_models.Attendance(user_id=user_id, date=date)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

# --- 특정 사용자의 모든 출석 기록 조회 ---
def get_all_attendances_by_user(db: Session, user_id: int):
    return db.query(db_models.Attendance).filter(
        db_models.Attendance.user_id == user_id
    ).order_by(db_models.Attendance.date.asc()).all()