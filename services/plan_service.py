from models.plan_model import LearningPlanRequest, LearningPlanInternal
from db.plan_supabase import save_learning_plan_to_db, get_latest_plan_by_user
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

    #학습 계획 정보 표시
    summary_lines = []

    summary_lines.append(f"총 소요 일수 : {estimated_days}일")
    summary_lines.append(f"학습 주기 : {frequency_description}")
    summary_lines.append(f"총 학습 시간 : {total_duration}분")

    style_names = {
        "conversation": "회화 학습",
        "grammar": "문법 연습",
        "pronunciation": "발음 연습"
    }

    if time_distribution.get("conversation", 0) > 0:
        summary_lines.append(f"{style_names['conversation']} : {time_distribution['conversation']}분")
    if time_distribution.get("grammar", 0) > 0:
        summary_lines.append(f"{style_names['grammar']} : {time_distribution['grammar']}분")
    if time_distribution.get("pronunciation", 0) > 0:
        summary_lines.append(f"{style_names['pronunciation']} : {time_distribution['pronunciation']}분")

    plan_summary = "\n".join(summary_lines)

    internal_plan = LearningPlanInternal(
        user_id=request.user_id,
        user_level=request.current_level,
        goal_level=request.goal_level,
        estimated_days=estimated_days,
        frequency_description=frequency_description,
        total_session_duration=total_duration,
        time_distribution=time_distribution,
        plan_summary=plan_summary
    )

    return internal_plan.dict()

# 학습 계획 DB 저장
def save_learning_plan(plan_data: dict) -> list:
    if 'time_distribution' in plan_data and isinstance(plan_data['time_distribution'], dict):
        plan_data['time_distribution'] = json.dumps(plan_data['time_distribution'])
    return save_learning_plan_to_db(plan_data)

def get_and_process_latest_plan(user_id: str):
    """
    최신 학습 계획을 가져온 후, time_distribution 필드를
    문자열에서 딕셔너리로 변환합니다.
    """
    plan_data = get_latest_plan_by_user(user_id)
    if plan_data and isinstance(plan_data.get('time_distribution'), str):
        try:
            # JSON 문자열을 파이썬 딕셔너리로 변환
            plan_data['time_distribution'] = json.loads(plan_data['time_distribution'])
        except json.JSONDecodeError:
            # 파싱 실패 시 기본값으로 대체
            plan_data['time_distribution'] = {}

    return plan_data
