from fastapi import APIRouter, HTTPException, Path
from models.statistics_model import StatisticsResponse, User
from db.statistics_supabase import get_user_data_from_supabase
from services.statistics_service import calculate_overall_statistics, calculate_progress_statistics

router = APIRouter()

@router.get("/statistics/{user_id}", response_model=StatisticsResponse)

def get_user_statistics(user_id: str = Path(..., title="사용자 ID", description="통계를 조회할 사용자의 고유 ID")):
    user_data = get_user_data_from_supabase(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user = User(**user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing user data: {e}")


    overall_stats = calculate_overall_statistics(user.learning_logs)


    progress_stats = None
    if user.learning_goals:
        progress_stats = calculate_progress_statistics(user.learning_logs, user.learning_goals)


    return StatisticsResponse(
        overall_statistics=overall_stats,
        progress_statistics=progress_stats
    )