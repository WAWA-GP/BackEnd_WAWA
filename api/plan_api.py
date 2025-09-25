from fastapi import APIRouter, HTTPException, Depends

from core.dependencies import get_current_user
from db.plan_supabase import get_latest_plan_by_user
from models.plan_model import LearningPlanRequest, LearningPlanResponse
from models.login_model import UserProfileResponse
from models.statistics_model import LearningGoal
from services.plan_service import create_custom_learning_plan, save_learning_plan
from db.statistics_supabase import update_user_learning_goal
from services import login_service, plan_service
from services.performance_monitor import measure_performance
from api.login_api import oauth2_scheme
from db.login_supabase import get_supabase_client
from supabase import Client as AsyncClient
import json

router = APIRouter()

@router.post("/create", response_model=UserProfileResponse)
@measure_performance("학습 계획 생성")
async def create_plan_endpoint(
        request: LearningPlanRequest,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        # 1. 학습 계획 생성
        plan_details = create_custom_learning_plan(request)

        # 👇 [수정] time_distribution이 딕셔너리일 때 미리 값을 추출합니다.
        time_dist = plan_details.get('time_distribution', {})
        new_goal = LearningGoal(
            conversation_goal=time_dist.get("conversation", 0),
            grammar_goal=time_dist.get("grammar", 0) // 10,
            pronunciation_goal=time_dist.get("pronunciation", 0) // 10
        )

        # 2. 이제 DB에 저장합니다. (이후에 time_dist를 사용하지 않으므로 안전)
        save_learning_plan(plan_details)

        # 3. user_id를 사용하여 학습 목표 업데이트 (기존 코드와 동일)
        # 👇 [수정] user_id를 request에서 직접 가져오도록 변경합니다.
        update_user_learning_goal(request.user_id, json.loads(new_goal.model_dump_json()))

        # 4. 저장 직후, 최신 프로필 정보를 다시 조회하여 반환 (기존 코드와 동일)
        updated_user_profile = await login_service.get_current_user(token, supabase)
        if not updated_user_profile:
            raise HTTPException(status_code=404, detail="업데이트 후 프로필을 조회할 수 없습니다.")

        return updated_user_profile

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=LearningPlanResponse)
async def get_latest_plan(current_user: dict = Depends(get_current_user)):
    """
    현재 로그인한 사용자의 가장 최근 학습 계획을 조회합니다.
    """
    user_id = current_user.get('user_id')

    # ▼▼▼ [수정] 새로운 서비스 함수를 호출합니다. ▼▼▼
    latest_plan = plan_service.get_and_process_latest_plan(user_id)

    if not latest_plan:
        raise HTTPException(status_code=404, detail="아직 생성된 학습 계획이 없습니다.")

    return latest_plan
