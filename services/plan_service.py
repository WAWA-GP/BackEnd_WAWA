from models.plan_model import LearningPlanRequest, LearningPlanInternal
from db.plan_supabase import save_learning_plan_to_db
import json

# 가중치 상수 정의
LEVEL_DIFFERENCE_WEIGHT = 10  # 레벨 차이 1당 소요 일수
DAILY_FREQUENCY_WEIGHT = -5   # 하루 학습 빈도 1회당 소요 일수 감소
INTERVAL_FREQUENCY_WEIGHT = 5 # 학습 간격 1일당 소요 일수 증가
SESSION_DURATION_WEIGHT = -0.5 # 학습 시간 1분당 소요 일수 감소


# 학습 상세 계산
def create_custom_learning_plan(request: LearningPlanRequest) -> dict:
    # 수준 차이 별 소요 일수
    level_diff = request.goal_level - request.current_level
    estimated_days = 30 + (level_diff * LEVEL_DIFFERENCE_WEIGHT)

    # 학습 빈도
    if request.frequency_type == 'daily':
        estimated_days += (request.frequency_value * DAILY_FREQUENCY_WEIGHT)
        frequency_description = f"하루에 {request.frequency_value}번 학습"
    else:
        estimated_days += (request.frequency_value * INTERVAL_FREQUENCY_WEIGHT)
        frequency_description = f"{request.frequency_value}일에 1번 학습"

    # 학습 소요 시간
    estimated_days += (request.session_duration_minutes * SESSION_DURATION_WEIGHT)
    estimated_days = max(7, int(estimated_days))

    # 학습 방식별 시간 분배
    styles = request.preferred_styles
    num_styles = len(styles)
    total_duration = request.session_duration_minutes

    time_distribution = {
        "conversation": 0,
        "grammar": 0,
        "pronunciation": 0
    }

    if num_styles > 0:
        base_time_per_style = total_duration / num_styles
        for style in time_distribution:
            if style in styles:
                time_distribution[style] = int(base_time_per_style)

        # 학습 시간 분배(회화 > 문법 > 발음 순)
        remainder = total_duration - sum(time_distribution.values())
        if remainder > 0 and "conversation" in styles:
            time_distribution["conversation"] += remainder
        elif remainder > 0 and "grammar" in styles:
            time_distribution["grammar"] += remainder
        elif remainder > 0 and "pronunciation" in styles:
            time_distribution["pronunciation"] += remainder


    internal_plan = LearningPlanInternal(
        user_id=request.user_id,
        user_level=request.current_level,
        goal_level=request.goal_level,
        estimated_days=estimated_days,
        frequency_description=frequency_description,
        total_session_duration=total_duration,
        time_distribution=time_distribution
    )

    return internal_plan.dict()

# 학습 계획 DB 저장
def save_learning_plan(plan_data: dict) -> list:
    if 'time_distribution' in plan_data and isinstance(plan_data['time_distribution'], dict):
        plan_data['time_distribution'] = json.dumps(plan_data['time_distribution'])
    return save_learning_plan_to_db(plan_data)

