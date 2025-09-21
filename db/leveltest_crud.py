# 'LevelTest' 관련 모델에 대한 데이터베이스 CRUD 작업을 정의하는 파일입니다.
from sqlalchemy.orm import Session
from database import models as db_models

# --- 모든 레벨 테스트 문제 조회 ---
def get_all_questions(db: Session):
    return db.query(db_models.LevelTestQuestion).all()

# --- 레벨 테스트 결과 생성 ---
def create_level_test_result(db: Session, user_id: int, score: int, level: str):
    db_result = db_models.LevelTestResult(user_id=user_id, score=score, level=level)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result