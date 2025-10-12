# models/challenge_model.py

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# --- Request Models --- (변경 없음)
class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    challenge_type: str # 'pronunciation', 'grammar', 'conversation'
    target_value: int = Field(..., gt=0)
    duration_days: int = Field(default=7, gt=0)

class ProgressLogRequest(BaseModel):
    log_type: str # 'pronunciation', 'grammar', 'conversation'
    value: int = Field(..., gt=0)


# --- Response Models ---
# ▼▼▼ [수정] ChallengeResponse 모델을 아래 코드로 교체 ▼▼▼
class ChallengeResponse(BaseModel):
    id: int
    group_id: int
    creator_id: str # 생성자 user_id
    creator_name: str # 생성자 이름
    title: str
    description: Optional[str]
    challenge_type: str
    target_value: int
    user_current_value: int # 개인의 현재 달성치
    is_completed: bool
    end_date: datetime
    is_active: bool
    created_at: datetime
# ▲▲▲ 수정 완료 ▲▲▲

class UserProgressResponse(BaseModel):
    user_id: str
    user_name: str
    current_value: int
    progress_percentage: float
    last_updated: datetime

class ChallengeDetailResponse(ChallengeResponse):
    leaderboard: List[UserProgressResponse]

class ChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)