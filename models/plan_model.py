from pydantic import BaseModel, Field
from typing import List, Dict

# API 요청
class LearningPlanRequest(BaseModel):
    user_id: str
    current_level: int = Field(..., gt=0, description="사용자의 현재 레벨")
    goal_level: int = Field(..., gt=0, description="사용자의 목표 레벨")
    frequency_type: str = Field(..., pattern="^(daily|interval)$", description="학습 빈도 타입 ('daily' or 'interval')")
    frequency_value: int = Field(..., gt=0, description="학습 빈도 값 (일 x회 또는 x일에 1번)")
    session_duration_minutes: int = Field(..., ge=10, le=120, description="1회 학습 소요 시간 (분)")
    preferred_styles: List[str] = Field(..., description="선호 학습 방식 리스트")

# DB 저장
class LearningPlanInternal(BaseModel):
    user_id: str
    user_level: int
    goal_level: int
    estimated_days: int
    frequency_description: str
    total_session_duration: int
    time_distribution: Dict[str, int]
    plan_summary: str

# API 응답
class LearningPlanResponse(BaseModel):
    id: int
    created_at: str
    user_id: str
    user_level: int
    goal_level: int
    estimated_days: int
    frequency_description: str
    total_session_duration: int
    time_distribution: Dict[str, int]
    plan_summary: str

    class Config:
        orm_mode = True

