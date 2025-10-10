# services/plan_service.py

from models.plan_model import LearningPlanRequest, LearningPlanInternal, DirectPlanRequest
from db.plan_supabase import save_learning_plan_to_db, get_latest_plan_by_user
from supabase import AsyncClient
import json
from typing import List, Dict
from fastapi import HTTPException

# 추천 플랜(템플릿) 정의 (수정 없음)
PREDEFINED_PLANS: Dict[str, Dict] = {
    "toeic_master": {
        "name": "TOEIC 900점 마스터",
        "description": "토익 고득점을 목표로 문법과 발음 위주로 집중 학습하는 플랜입니다.",
        "params": {
            "goal_level": 8, "frequency_type": "daily", "frequency_value": 1,
            "session_duration_minutes": 60, "preferred_styles": ["grammar", "pronunciation"]
        }
    },
    "daily_conversation": {
        "name": "매일 꾸준히 회화 연습",
        "description": "매일 짧은 시간이라도 회화 연습에 집중하여 유창성을 기르는 플랜입니다.",
        "params": {
            "goal_level": 5, "frequency_type": "daily", "frequency_value": 1,
            "session_duration_minutes": 20, "preferred_styles": ["conversation"]
        }
    },
    "balanced_growth": {
        "name": "균형 성장 플랜",
        "description": "회화, 문법, 발음 모든 영역을 골고루 학습하며 전반적인 실력을 향상시킵니다.",
        "params": {
            "goal_level": 6, "frequency_type": "interval", "frequency_value": 2,
            "session_duration_minutes": 45, "preferred_styles": ["conversation", "grammar", "pronunciation"]
        }
    }
}

# 학습 계획 계산에 사용되는 가중치 (수정 없음)
LEVEL_DIFFERENCE_WEIGHT = 10
DAILY_FREQUENCY_WEIGHT = -5
INTERVAL_FREQUENCY_WEIGHT = 5
SESSION_DURATION_WEIGHT = -0.5

def get_plan_templates() -> List[Dict[str, str]]:
    """추천 플랜 목록을 반환합니다."""
    template_list = []
    for id, plan in PREDEFINED_PLANS.items():
        template_list.append({"id": id, "name": plan["name"], "description": plan["description"]})
    return template_list

# 모든 계획 생성 로직의 기반이 되는 상세 계획 생성 함수 (수정 없음)
def _create_detailed_learning_plan(request: LearningPlanRequest) -> dict:
    level_diff = request.goal_level - request.current_level
    estimated_days = 30 + (level_diff * LEVEL_DIFFERENCE_WEIGHT)

    if request.frequency_type == 'daily':
        estimated_days += (request.frequency_value * DAILY_FREQUENCY_WEIGHT)
        frequency_description = f"하루에 {request.frequency_value}번 학습"
    else: # 'interval'
        estimated_days += (request.frequency_value * INTERVAL_FREQUENCY_WEIGHT)
        frequency_description = f"{request.frequency_value}일에 1번 학습"

    estimated_days += (request.session_duration_minutes * SESSION_DURATION_WEIGHT)
    estimated_days = max(7, int(estimated_days))

    styles = request.preferred_styles
    num_styles = len(styles)
    total_duration = request.session_duration_minutes
    time_distribution = {"conversation": 0, "grammar": 0, "pronunciation": 0}

    if num_styles > 0:
        base_time_per_style = total_duration / num_styles
        for style in time_distribution:
            if style in styles:
                time_distribution[style] = int(base_time_per_style)
        remainder = total_duration - sum(time_distribution.values())
        if remainder > 0 and styles:
            time_distribution[styles[0]] += remainder

    summary_lines = [
        f"총 소요 일수 : {estimated_days}일",
        f"학습 주기 : {frequency_description}",
        f"총 학습 시간 : {total_duration}분"
    ]
    style_names = {"conversation": "회화 학습", "grammar": "문법 연습", "pronunciation": "발음 연습"}
    for style, duration in time_distribution.items():
        if duration > 0:
            summary_lines.append(f"{style_names[style]} : {duration}분")

    plan_summary = "\n".join(summary_lines)

    internal_plan = LearningPlanInternal(
        user_id=request.user_id, user_level=request.current_level, goal_level=request.goal_level,
        estimated_days=estimated_days, frequency_description=frequency_description,
        total_session_duration=total_duration, time_distribution=time_distribution,
        plan_summary=plan_summary
    )
    return internal_plan.model_dump()


def create_plan_from_template(user_id: str, template_id: str, current_level: int) -> dict:
    """템플릿을 기반으로 학습 계획을 생성합니다."""
    template = PREDEFINED_PLANS.get(template_id)
    if not template:
        # [수정] 유효하지 않은 템플릿 ID에 대해 404 Not Found 예외 발생
        raise HTTPException(status_code=404, detail="선택한 추천 플랜을 찾을 수 없습니다.")

    plan_params = template["params"]
    full_request = LearningPlanRequest(
        user_id=user_id, current_level=current_level, goal_level=plan_params["goal_level"],
        frequency_type=plan_params["frequency_type"], frequency_value=plan_params["frequency_value"],
        session_duration_minutes=plan_params["session_duration_minutes"], preferred_styles=plan_params["preferred_styles"]
    )
    return _create_detailed_learning_plan(full_request)


def create_direct_learning_plan(user_id: str, current_level: int, request: DirectPlanRequest) -> dict:
    """간소화된 직접 설정값으로 학습 계획을 생성합니다."""
    full_request = LearningPlanRequest(
        user_id=user_id,
        current_level=current_level,
        goal_level=current_level + 2,
        frequency_type='daily',
        frequency_value=1,
        session_duration_minutes=request.session_duration_minutes,
        preferred_styles=request.preferred_styles
    )
    # ▼▼▼ [오류 수정] 올바른 함수 이름으로 호출합니다. ▼▼▼
    return _create_detailed_learning_plan(full_request)


async def save_learning_plan(plan_data: dict, db: AsyncClient) -> list:
    if 'time_distribution' in plan_data and isinstance(plan_data['time_distribution'], dict):
        plan_data['time_distribution'] = json.dumps(plan_data['time_distribution'])
    return await save_learning_plan_to_db(plan_data, db)


async def get_and_process_latest_plan(user_id: str, db: AsyncClient):
    plan_data = await get_latest_plan_by_user(user_id, db)
    if plan_data and isinstance(plan_data.get('time_distribution'), str):
        try:
            plan_data['time_distribution'] = json.loads(plan_data['time_distribution'])
        except json.JSONDecodeError:
            plan_data['time_distribution'] = {}
    return plan_data