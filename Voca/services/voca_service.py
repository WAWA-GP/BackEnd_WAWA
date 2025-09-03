import db.supabase_client as db
from models.voca_models import VocaItem
from typing import List

def get_voca(user_id: str) -> list:
    """사용자의 전체 단어장을 조회하는 서비스 함수."""
    return db.get_user_voca_from_db(user_id)

def add_voca(user_id: str, word_to_add: str, memo: str) -> dict:
    word_info = db.search_word_in_dictionary(word_to_add)
    if not word_info:
        return {"status": "error", "message": "단어 조회 실패"}

    current_voca = db.get_user_voca_from_db(user_id)
    if any(entry['word'].lower() == word_to_add.lower() for entry in current_voca):
        return {"status": "error", "message": f"중복 단어 존재."}

    new_entry = VocaItem(**word_info, memo=memo).dict()
    current_voca.append(new_entry)

    success = db.update_user_voca_in_db(user_id, current_voca)
    if success:
        return {"status": "success", "message": "단어 추가 성공", "data": new_entry}
    return {"status": "error", "message": "DB 업데이트 실패"}


def update_voca(user_id: str, word: str, new_memo: str) -> dict:
    """단어장의 특정 단어에 대한 메모를 수정하는 서비스 함수."""
    voca = db.get_user_voca_from_db(user_id)
    word_found = False
    for entry in voca:
        if entry['word'].lower() == word.lower():
            entry['memo'] = new_memo
            word_found = True
            break
    if not word_found:
        return {"status": "error", "message": "수정 대상 없음"}

    success = db.update_user_voca_in_db(user_id, voca)
    return {"status": "success", "message": "단어 수정 성공"} if success else {"status": "error", "message": "DB 업데이트 실패"}


def delete_voca(user_id: str, word: str) -> dict:
    """사용자 단어장에서 특정 단어를 삭제하는 서비스 함수."""
    voca = db.get_user_voca_from_db(user_id)
    original_length = len(voca)
    new_voca = [entry for entry in voca if entry['word'].lower() != word.lower()]
    if len(new_voca) == original_length:
        return {"status": "error", "message": "삭제 대상 없음"}

    success = db.update_user_voca_in_db(user_id, new_voca)
    return {"status": "success", "message": "단어 삭제 성공"} if success else {"status": "error", "message": "DB 업데이트 실패"}


def sync_voca(user_id: str, new_voca_data: List[VocaItem]) -> dict:
    """클라이언트의 단어장 전체를 서버에 동기화(덮어쓰기)하는 서비스 함수."""
    voca_list_of_dict = [item.dict() for item in new_voca_data]
    success = db.update_user_voca_in_db(user_id, voca_list_of_dict)
    return {"status": "success", "message": "단어장 동기화 완료"} if success else {"status": "error", "message": "단어장 동기화 실패"}