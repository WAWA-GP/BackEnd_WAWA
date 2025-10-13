# api/points_api.py
from fastapi import APIRouter, Depends
from models.point_model import PointTransactionRequest
from services import point_service
from core.database import get_db # get_db 함수를 import
from supabase import AsyncClient # 타입 명시

router = APIRouter()

# 엔드포인트를 비동기(async)로 변경하고, Depends(get_db)를 사용
@router.post("/transaction", response_model=dict)
async def execute_point_transaction(request: PointTransactionRequest, db: AsyncClient = Depends(get_db)):
    """포인트 적립 또는 사용 API 엔드포인트"""
    # 서비스 함수 호출 시 db 클라이언트를 전달
    return await point_service.process_point_transaction(request, db)