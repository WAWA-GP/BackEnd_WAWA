from sqlalchemy import (
    Column, Integer, String, Boolean, Text,
    Date, DateTime, ForeignKey, UniqueConstraint
)
from datetime import datetime, date
from sqlalchemy.orm import relationship
from app.database import Base


# ======================
# ✅ 사용자(User)
# ======================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # ✅ 논리 삭제용 플래그

    native_language = Column(String, nullable=True)
    learning_language = Column(String, nullable=True)
    level = Column(String, default="beginner")  # ← 레벨 테스트 결과로만 변경됨

    # ✅ 관계 설정
    level_test_results = relationship("LevelTestResult", back_populates="user")
    attendances = relationship("Attendance", back_populates="user")


# ======================
# ✅ 공지사항(Notice)
# ======================
class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ======================
# ✅ FAQ
# ======================
class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(300), nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ======================
# ✅ 레벨 테스트 문제(LevelTestQuestion)
# ======================
class LevelTestQuestion(Base):
    __tablename__ = "level_test_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1=초급, 2=중급, 3=고급


# ======================
# ✅ 레벨 테스트 결과(LevelTestResult)
# ======================
class LevelTestResult(Base):
    __tablename__ = "level_test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    score = Column(Integer, nullable=False)
    level = Column(String, nullable=False)  # beginner / intermediate / advanced

    # ✅ User와 연결
    user = relationship("User", back_populates="level_test_results")


# ======================
# ✅ 출석체크(Attendance)
# ======================
class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 같은 유저가 같은 날짜에 중복 출석 불가
    __table_args__ = (UniqueConstraint("user_id", "date", name="_user_date_uc"),)

    # ✅ User와 연결
    user = relationship("User", back_populates="attendances")