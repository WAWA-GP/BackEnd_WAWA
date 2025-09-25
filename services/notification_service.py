# services/notification_service.py

from supabase import AsyncClient
from db import notification_supabase, user_crud  # user_crud import 추가
from pyfcm import FCMNotification

# --- 1. 공부 시작 알림 생성 서비스 ---
async def send_study_start_notification(db: AsyncClient, email: str):
    """지정된 이메일의 사용자에게 학습 시작을 독려하는 알림을 보냅니다."""
    # get_user_by_username를 사용해 사용자 정보 조회
    user = await user_crud.get_user_by_username(db, username=email)
    if not user:
        print(f"사용자를 찾을 수 없습니다: {email}")
        return

    user_id = user.get('user_id')
    content = "오늘의 회화 학습, 시작해볼까요? 새로운 문장이 기다리고 있어요! 🚀"
    await notification_supabase.create_notification(db, user_id, 'start', content)


# --- 2. 공부 현황 알림 생성 서비스 ---
async def send_progress_notification(db: AsyncClient, email: str, progress_percent: int):
    """지정된 이메일의 사용자의 학습 현황을 알려주는 알림을 보냅니다."""
    # get_user_by_username를 사용해 사용자 정보 조회
    user = await user_crud.get_user_by_username(db, username=email)
    if not user:
        print(f"사용자를 찾을 수 없습니다: {email}")
        return

    user_id = user.get('user_id')
    # 조회된 사용자 정보에서 이름을 가져와 메시지에 사용
    user_name = user.get('name', '학습자') # 이름이 없을 경우 '학습자'로 표시

    content = f"{user_name}님, 벌써 {progress_percent}%나 진행했어요. 정말 대단해요! 👍"
    await notification_supabase.create_notification(db, user_id, 'progress', content)


# --- 3. 복습 알림 생성 서비스 ---
async def send_review_notification(db: AsyncClient, email: str, sentence_count: int):
    """지정된 이메일의 사용자에게 복습할 문장이 있음을 알리는 알림을 보냅니다."""
    # get_user_by_username를 사용해 사용자 정보 조회
    user = await user_crud.get_user_by_username(db, username=email)
    if not user:
        print(f"사용자를 찾을 수 없습니다: {email}")
        return

    user_id = user.get('user_id')
    content = f"잊기 전에 복습해봐요! 복습할 문장이 {sentence_count}개 있어요. 📚"
    await notification_supabase.create_notification(db, user_id, 'review', content)

# --- 특정 사용자 알림 목록 조회 서비스 ---
async def get_all_notifications_for_user(db: AsyncClient, user_id: str, skip: int, limit: int):
    """특정 사용자의 알림 목록을 데이터베이스에서 가져옵니다."""
    return await notification_supabase.get_notifications_by_user(db, user_id, skip, limit)

# --- 알림 읽음 처리 서비스 ---
async def mark_as_read(db: AsyncClient, notification_id: int, current_user_id: str):
    """알림을 읽음 처리하되, 해당 알림이 현재 로그인한 사용자의 것인지 확인합니다."""
    notification = await notification_supabase.get_notification_by_id(db, notification_id)
    # 알림이 없거나, 다른 사람의 알림을 수정하려는 경우 None을 반환
    if not notification or notification.get('user_id') != current_user_id:
        return None
    return await notification_supabase.mark_notification_as_read(db, notification_id)
