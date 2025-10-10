# api/plan_api.py

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from core.dependencies import get_current_user
from core.database import get_db
from supabase import AsyncClient

from db.plan_supabase import update_learning_plan_in_db, get_latest_plan_by_user
from db.statistics_supabase import update_user_learning_goal
from models.plan_model import LearningPlanResponse, PlanTemplateResponse, SelectPlanTemplateRequest, DirectPlanRequest
from models.login_model import UserProfileResponse
from models.statistics_model import LearningGoal
from services.plan_service import save_learning_plan, get_plan_templates, create_plan_from_template, \
    create_direct_learning_plan, get_and_process_latest_plan
from services import login_service
from services.performance_monitor import measure_performance
from api.login_api import oauth2_scheme
from db.login_supabase import get_supabase_client
import json


router = APIRouter()

CEFR_TO_NUMERIC_LEVEL = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}

@router.get("/templates", response_model=List[PlanTemplateResponse])
def get_templates_endpoint():
    return get_plan_templates()

@router.post("/select-template", response_model=UserProfileResponse)
@measure_performance("템플릿으로 학습 계획 생성")
async def select_template_endpoint(
        request: SelectPlanTemplateRequest,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client),
        db: AsyncClient = Depends(get_db)
):
    try:
        user_profile = await login_service.get_current_user(token, supabase)
        if not user_profile:
            raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")

        assessed_level_str = user_profile.get('assessed_level')
        current_level = CEFR_TO_NUMERIC_LEVEL.get(assessed_level_str, 1)

        plan_details = create_plan_from_template(request.user_id, request.template_id, current_level)

        time_dist = plan_details.get('time_distribution', {})
        new_goal = LearningGoal(
            conversation_goal=time_dist.get("conversation", 0),
            grammar_goal=time_dist.get("grammar", 0) // 10,
            pronunciation_goal=time_dist.get("pronunciation", 0) // 10
        )

        await save_learning_plan(plan_details, db)
        await update_user_learning_goal(request.user_id, json.loads(new_goal.model_dump_json()), db)

        updated_user_profile = await login_service.get_current_user(token, supabase)
        if not updated_user_profile:
            raise HTTPException(status_code=404, detail="업데이트 후 프로필을 조회할 수 없습니다.")

        return updated_user_profile
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", response_model=UserProfileResponse)
@measure_performance("학습 계획 생성")
async def create_plan_endpoint(
        # ▼▼▼ [오류 수정] 변수 이름을 'request'에서 'plan_data'로 변경 ▼▼▼
        plan_data: DirectPlanRequest,
        token: str = Depends(oauth2_scheme),
        supabase: AsyncClient = Depends(get_supabase_client),
        db: AsyncClient = Depends(get_db)
):
    try:
        user_profile = await login_service.get_current_user(token, supabase)
        if not user_profile:
            raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")

        user_id = user_profile.get('user_id')
        current_level_str = user_profile.get('assessed_level')
        current_level = CEFR_TO_NUMERIC_LEVEL.get(current_level_str, 1)

        # ▼▼▼ [오류 수정] 변경된 변수 이름으로 서비스 함수 호출 ▼▼▼
        plan_details = create_direct_learning_plan(user_id, current_level, plan_data)

        time_dist = plan_details.get('time_distribution', {})
        new_goal = LearningGoal(
            conversation_goal=time_dist.get("conversation", 0),
            grammar_goal=time_dist.get("grammar", 0) // 10,
            pronunciation_goal=time_dist.get("pronunciation", 0) // 10
        )

        await save_learning_plan(plan_details, db)
        await update_user_learning_goal(user_id, json.loads(new_goal.model_dump_json()), db)

        updated_user_profile = await login_service.get_current_user(token, supabase)
        if not updated_user_profile:
            raise HTTPException(status_code=404, detail="업데이트 후 프로필을 조회할 수 없습니다.")

        return updated_user_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# [추가] 학습 계획 수정을 위한 PUT 엔드포인트
@router.put("/{plan_id}", response_model=LearningPlanResponse)
@measure_performance("학습 계획 수정")
async def update_plan_endpoint(
        plan_id: int,
        plan_data: DirectPlanRequest,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    try:
        user_id = current_user.get('user_id')
        current_level_str = current_user.get('assessed_level')
        current_level = CEFR_TO_NUMERIC_LEVEL.get(current_level_str, 1)

        # 1. 수정하려는 계획이 현재 사용자의 것인지 확인 (보안)
        #    (get_latest_plan_by_user를 사용하거나, get_plan_by_id 함수를 만들어 사용)
        #    여기서는 가장 최근 계획만 수정 가능하다고 가정.
        latest_plan = await get_latest_plan_by_user(user_id, db)
        if not latest_plan or latest_plan['id'] != plan_id:
            raise HTTPException(status_code=403, detail="수정 권한이 없거나 유효하지 않은 계획 ID입니다.")

        # 2. 새로운 요청 데이터로 계획을 다시 계산 (기존 서비스 재활용)
        updated_plan_details = create_direct_learning_plan(user_id, current_level, plan_data)

        # 3. 계산된 새 목표(Goal)를 user_profiles 테이블에 업데이트
        time_dist = updated_plan_details.get('time_distribution', {})
        new_goal = LearningGoal(
            conversation_goal=time_dist.get("conversation", 0),
            grammar_goal=time_dist.get("grammar", 0) // 10,
            pronunciation_goal=time_dist.get("pronunciation", 0) // 10
        )
        await update_user_learning_goal(user_id, json.loads(new_goal.model_dump_json()), db)

        # 4. learning_plans 테이블에 변경된 내용 업데이트
        if 'time_distribution' in updated_plan_details and isinstance(updated_plan_details['time_distribution'], dict):
            updated_plan_details['time_distribution'] = json.dumps(updated_plan_details['time_distribution'])

        updated_plan = await update_learning_plan_in_db(plan_id, updated_plan_details, db)

        if not updated_plan:
            raise HTTPException(status_code=500, detail="학습 계획 업데이트에 실패했습니다.")

        # Supabase에서 JSON 문자열로 반환된 time_distribution을 다시 dict로 변환
        if isinstance(updated_plan.get('time_distribution'), str):
            updated_plan['time_distribution'] = json.loads(updated_plan['time_distribution'])

        return updated_plan

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/latest", response_model=LearningPlanResponse)
async def get_latest_plan(
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    user_id = current_user.get('user_id')
    latest_plan = await get_and_process_latest_plan(user_id, db)

    if not latest_plan:
        raise HTTPException(status_code=404, detail="아직 생성된 학습 계획이 없습니다.")

    return latest_plan