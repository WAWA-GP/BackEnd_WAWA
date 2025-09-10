import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# Supabase 클라이언트 초기화
url: Optional[str] = os.environ.get("SUPABASE_URL")
key: Optional[str] = os.environ.get("SUPABASE_KEY")

# URL 또는 KEY가 없는 경우 예외 처리
if not url or not key:
    raise ValueError("Supabase URL 또는 Key가 .env 파일에 설정되지 않았습니다.")

supabase: Client = create_client(url, key)


def create_notification(user_id: str, notif_type: str, content: str) -> Dict[str, Any]:
    """
    Supabase 'notifications' 테이블에 새로운 알림을 추가하는 공통 함수

    Args:
        user_id (str): 알림을 받을 사용자의 UUID
        notif_type (str): 알림 종류 ('start', 'progress', 'review' 등)
        content (str): 알림 내용

    Returns:
        Dict[str, Any]: Supabase로부터 반환된 결과 딕셔너리
    """
    try:
        data, count = supabase.table('notifications').insert({
            'user_id': user_id,
            'type': notif_type,
            'content': content
        }).execute()

        print(f"알림 생성 성공: User {user_id}, Type {notif_type}")
        return {"success": True, "data": data}
    except Exception as e:
        print(f"알림 생성 실패: {e}")
        return {"success": False, "error": str(e)}


# 1. 공부 시작 알림 생성
def send_study_start_notification(user_id: str):
    """지정된 사용자에게 학습 시작을 독려하는 알림을 보냅니다."""
    content = "오늘의 회화 학습, 시작해볼까요? 새로운 문장이 기다리고 있어요! 🚀"
    create_notification(user_id, 'start', content)


# 2. 공부 현황 알림 생성
def send_progress_notification(user_id: str, user_name: str, progress_percent: int):
    """사용자의 학습 현황을 알려주는 알림을 보냅니다."""
    content = f"{user_name}님, 벌써 {progress_percent}%나 진행했어요. 정말 대단해요! 👍"
    create_notification(user_id, 'progress', content)


# 3. 복습 알림 생성
def send_review_notification(user_id: str, sentence_count: int):
    """복습할 문장이 있음을 알리는 알림을 보냅니다."""
    content = f"잊기 전에 복습해봐요! 복습할 문장이 {sentence_count}개 있어요. 📚"
    create_notification(user_id, 'review', content)


""" 
main.py 부분
# notice 모듈에서 필요한 함수들을 가져옵니다.
from notice import (
    send_study_start_notification,
    send_progress_notification,
    send_review_notification
)

def main_flow():

앱의 메인 로직을 시뮬레이션하는 예시 함수

# --- 예시 시나리오 ---
# 실제 앱에서는 사용자가 로그인하거나 특정 조건을 만족했을 때 호출됩니다.

# 더미 사용자 정보
current_user_id = "사용자의_UUID"  # 예: "a1b2c3d4-e5f6-..."
current_user_name = "김와와"

print("메인 로직 시작...")

# 1. 사용자가 앱을 켰을 때 (또는 특정 시간대에) 학습 시작 알림 보내기
# 예: 하루에 한 번, 사용자가 처음 앱을 실행했을 때
print("\n[상황 1: 학습 시작 알림 보내기]")
send_study_start_notification(user_id=current_user_id)

# 2. 사용자가 특정 챕터를 완료했을 때 진행도 알림 보내기
# 예: 전체 학습량의 50%를 달성
print("\n[상황 2: 학습 현황 알림 보내기]")
send_progress_notification(
    user_id=current_user_id,
    user_name=current_user_name,
    progress_percent=50
)

# 3. 복습할 시기가 된 문장이 있을 때 복습 알림 보내기
# 예: 에빙하우스 망각 곡선에 따라 3일이 지난 문장 5개가 있을 경우
print("\n[상황 3: 복습 알림 보내기]")
send_review_notification(user_id=current_user_id, sentence_count=5)

print("\n메인 로직 종료.")


if __name__ == "__main__":
main_flow() 
"""