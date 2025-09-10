from fastapi import APIRouter, HTTPException
from models.plan_model import LearningPlanRequest, LearningPlanResponse
from services.plan_service import create_custom_learning_plan, save_learning_plan
import json

router = APIRouter()

@router.post("/create", response_model=LearningPlanResponse)

def create_plan_endpoint(request: LearningPlanRequest):
    try:
        plan_details = create_custom_learning_plan(request)

        saved_data = save_learning_plan(plan_details)
        if not saved_data:
            raise HTTPException(status_code=500, detail="Failed to save the learning plan.")


        db_response = saved_data[0]

        if 'time_distribution' in db_response and isinstance(db_response['time_distribution'], str):
            db_response['time_distribution'] = json.loads(db_response['time_distribution'])
        return LearningPlanResponse.model_validate(db_response)

    except Exception as e:
        print(f"An error occurred while creating the plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

