from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LevelTestQuestion, LevelTestResult, User as DBUser
from app.utils.deps import get_current_user
import random

router = APIRouter(
    prefix="/level-test",
    tags=["Level Test"]
)

# ✅ 1. 문제 가져오기 (랜덤 10개)
@router.get("/questions")
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(LevelTestQuestion).all()
    if not questions:
        return {"message": "레벨 테스트 문제가 없습니다."}

    # 전체 문제 중 10개 랜덤 추출 (문제가 10개 미만이면 전체 반환)
    selected = random.sample(questions, min(10, len(questions)))
    return {"questions": selected}

# ✅ 2. 답안 제출하기
@router.post("/submit")
def submit_answers(
        answers: dict,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user)
):
    questions = db.query(LevelTestQuestion).all()
    score = 0
    for q in questions:
        if str(q.id) in answers and answers[str(q.id)] == q.correct_answer:
            score += 1

    total = len(questions)
    percentage = (score / total) * 100 if total > 0 else 0

    # 퍼센트 기반 레벨 판정
    if percentage < 40:
        level = "beginner"
    elif percentage < 70:
        level = "intermediate"
    else:
        level = "advanced"

    # 결과 저장
    result = LevelTestResult(user_id=current_user.id, score=score, level=level)
    db.add(result)

    # 사용자 프로필에 학습 레벨 반영
    current_user.level = level
    db.commit()

    return {"score": score, "level": level, "percentage": percentage}

# ✅ 3. 전체 결과 조회하기
@router.get("/results")
def get_results(
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user)
):
    results = db.query(LevelTestResult).filter(LevelTestResult.user_id == current_user.id).all()
    if not results:
        return {"message": "레벨 테스트 결과가 없습니다."}

    return {"results": results}