from sqlalchemy import Column, Integer, String, Boolean, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
from sqlalchemy.orm import relationship
from app.database import Base

Base = declarative_base()

# ✅ 사용자 DB 모델
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # ✅ 논리 삭제용 플래그

    native_language = Column(String, nullable=True)
    learning_language = Column(String, nullable=True)
    level = Column(String, default="beginner")  # ← 수동 수정 불가, 테스트 결과로만 변경

    # ✅ 프로필 및 레벨 테스트 결과 연동
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    level_test_results = relationship("LevelTestResult", back_populates="user")

# ✅ 공지사항 DB 모델
class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ✅ FAQ DB 모델
class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(300), nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ✅ 레벨 테스트 문제/결과
class LevelTestQuestion(Base):
    __tablename__ = "level_test_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1=초급, 2=중급, 3=고급

class LevelTestResult(Base):
    __tablename__ = "level_test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer, nullable=False)
    level = Column(String, nullable=False)  # beginner / intermediate / advanced

# 출석체크
class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 같은 유저가 같은 날짜에 중복 출석 불가
    __table_args__ = (UniqueConstraint("user_id", "date", name="_user_date_uc"),)

    # 관계 설정
    user = relationship("User", back_populates="attendances")