from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

# 학습 목표
class LearningGoal(BaseModel):
    conversation_goal: int = Field(0, description="회화 학습 목표 시간(분)")
    grammar_goal: int = Field(0, description="문법 연습 목표 횟수")
    pronunciation_goal: int = Field(0, description="발음 연습 목표 횟수")
    created_at: datetime = Field(default_factory=datetime.now)

# 학습 로그
class LearningLog(BaseModel):
    log_type: str = Field(..., description="학습 유형 (conversation, grammar, pronunciation)")
    duration: Optional[int] = Field(None, description="학습 시간(분), 회화 학습에만 해당")
    count: Optional[int] = Field(None, description="학습 횟수, 문법/발음 연습에만 해당")
    created_at: datetime = Field(default_factory=datetime.now)

# 사용자 정보
class User(BaseModel):
    user_id: str
    learning_goals: Optional[LearningGoal] = None
    learning_logs: list[LearningLog] = []

# 전체 누적 통계
class OverallStats(BaseModel):
    total_conversation_duration: int = 0
    total_grammar_count: int = 0
    total_pronunciation_count: int = 0

# 목표 대비 진척도 통계
class ProgressStats(BaseModel):
    conversation_progress: float = 0.0
    grammar_progress: float = 0.0
    pronunciation_progress: float = 0.0

# 학습 통계
class StatisticsResponse(BaseModel):
    overall_statistics: OverallStats
    progress_statistics: Optional[ProgressStats] = None