# models/point_model.py
# 포인트 거래 요청 시 필요한 데이터 구조 정의

from pydantic import BaseModel
from uuid import UUID

class PointTransactionRequest(BaseModel):
    user_id: UUID
    amount: int
    reason: str