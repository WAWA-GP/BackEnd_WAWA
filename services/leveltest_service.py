# '레벨 테스트' 관련 비즈니스 로직을 처리하는 파일입니다.
import random
from sqlalchemy.orm import Session
from models import leveltest_model
from db import leveltest_crud, user_crud

# --- 랜덤 문제 조회 서비스 ---
def get_random_questions(db: Session, count: int):
    questions = level_test_crud.get_all_questions(db)
    if not questions:
        return []
    return random.sample(questions, min(count, len(questions)))

# --- 답안 제출 및 채점 서비스 ---
def process_submission(db: Session, user_id: int, submission: level_test_model.LevelTestSubmit):
    score = 0
    question_map = {q.id: q.correct_answer for q in level_test_crud.get_all_questions(db)}

    for answer in submission.answers:
        if question_map.get(answer.question_id) == answer.submitted_answer:
            score += 1

    total = len(question_map)
    percentage = (score / total) * 100 if total > 0 else 0

    if percentage < 40:
        level = "beginner"
    elif percentage < 70:
        level = "intermediate"
    else:
        level = "advanced"

    result = level_test_crud.create_level_test_result(
        db=db, user_id=user_id, score=score, level=level
    )

    user_crud.update_user(db=db, user_id=user_id, update_data={"level": level})

    return result