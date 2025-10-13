# models/grammar_model.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ▼▼▼ [수정] API 응답 모델 변경 ▼▼▼
class GrammarHistoryResponse(BaseModel):
    id: int
    transcribed_text: str
    corrected_text: str
    grammar_feedback: Optional[List[str]] = []
    vocabulary_suggestions: Optional[List[str]] = []
    created_at: datetime
    is_favorite: Optional[bool] = False

class GrammarSessionCreate(BaseModel):
    transcribed_text: str
    corrected_text: str
    grammar_feedback: Optional[List[str]] = []
    vocabulary_suggestions: Optional[List[str]] = []

# (기존 GrammarStatistics 모델은 변경 없음)
class GrammarStatistics(BaseModel):
    total_count: int
    # 통계 모델은 당장 수정하지 않아도 동작하지만,
    # 추후 '정답률' 대신 '교정 발생률' 등으로 고도화할 수 있습니다.
    correct_count: int
    incorrect_count: int
    accuracy: float
    recent_accuracy: Optional[float] = None
