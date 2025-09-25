# models/notification_model.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- API 응답에 사용될 알림 정보 스키마 ---
# 클라이언트(앱)에 알림 정보를 보여줄 때 이 형식을 사용합니다.
class NotificationResponse(BaseModel):
    id: int
    user_id: str
    type: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True # DB 모델 객체를 Pydantic 모델로 변환
