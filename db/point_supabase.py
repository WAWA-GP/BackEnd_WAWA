# db/point_supabase.py
from uuid import UUID
from supabase import AsyncClient # AsyncClient 타입을 명시하기 위해 import

# supabase 클라이언트를 인자로 받고, 함수를 비동기(async)로 변경
async def update_points_and_log(db: AsyncClient, user_id: UUID, amount: int, reason: str):
    """RPC를 호출하여 포인트를 변경하고 내역을 기록합니다."""

    result = await db.rpc('handle_point_change', {
        'user_id_input': str(user_id),
        'change_amount_input': amount,
        'reason_text': reason
    }).execute()

    return result.data