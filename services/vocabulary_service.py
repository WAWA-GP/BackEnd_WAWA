# services/vocabulary_service.py

from supabase import AsyncClient
from db import vocabulary_supabase
from models import vocabulary_model
from fastapi import HTTPException

# --- Wordbook ---
async def create_new_wordbook(db: AsyncClient, name: str, user_id: str):
    return await vocabulary_supabase.create_wordbook(db, name, user_id)

async def get_user_wordbooks(db: AsyncClient, user_id: str):
    wordbooks = await vocabulary_supabase.get_wordbooks_by_user(db, user_id)
    # Pydantic 모델에 맞게 데이터 가공
    return [
        vocabulary_model.WordbookResponse(
            id=wb['id'],
            user_id=wb['user_id'],
            name=wb['name'],
            created_at=wb['created_at'],
            word_count=wb['word_count']
        ) for wb in wordbooks
    ]

# --- UserWord ---
async def add_new_word(db: AsyncClient, word: vocabulary_model.UserWordCreate, wordbook_id: int):
    return await vocabulary_supabase.add_word_to_wordbook(db, word, wordbook_id)

async def update_word_content(db: AsyncClient, word_id: int, word_update_data: vocabulary_model.UserWordContentUpdate):
    update_data = word_update_data.model_dump()
    return await vocabulary_supabase.update_word_details(db, word_id, update_data)

async def get_full_wordbook(db: AsyncClient, wordbook_id: int, user_id: str):
    wordbook_data = await vocabulary_supabase.get_wordbook_with_words(db, wordbook_id, user_id)
    if not wordbook_data:
        # [수정] 단어장이 없을 경우, None 대신 404 예외 발생
        raise HTTPException(status_code=404, detail="요청한 단어장을 찾을 수 없습니다.")

    wordbook_data['words'] = wordbook_data.get('user_words', [])
    return vocabulary_model.WordbookDetailResponse.model_validate(wordbook_data)


async def toggle_word_memorized(db: AsyncClient, word_id: int, is_memorized: bool):
    return await vocabulary_supabase.update_word_status(db, word_id, is_memorized)

async def remove_word_from_wordbook(db: AsyncClient, word_id: int):
    # [수정] 삭제 결과에 따라 처리
    deleted_word = await vocabulary_supabase.delete_word(db, word_id)
    if not deleted_word:
        raise HTTPException(status_code=404, detail="삭제할 단어를 찾을 수 없습니다.")
    return deleted_word

async def add_new_words_batch(db: AsyncClient, words_in: vocabulary_model.UserWordBatchCreate, wordbook_id: int):
    # 각 단어 데이터에 wordbook_id를 추가해줍니다.
    words_to_insert = []
    for word in words_in.words:
        word_dict = word.model_dump()
        word_dict['wordbook_id'] = wordbook_id
        words_to_insert.append(word_dict)

    return await vocabulary_supabase.add_words_to_wordbook_batch(db, words_to_insert)

async def delete_user_wordbook(db: AsyncClient, wordbook_id: int, user_id: str):
    # [수정] Supabase 함수가 삭제된 행의 수를 반환한다고 가정하고, 결과에 따라 처리
    deleted_wordbook = await vocabulary_supabase.delete_wordbook(db, wordbook_id, user_id)
    if not deleted_wordbook:
        # 삭제가 실패했거나, 대상이 없거나, 권한이 없는 경우
        raise HTTPException(status_code=404, detail="단어장을 삭제할 수 없거나 찾을 수 없습니다.")
    return deleted_wordbook

async def toggle_word_favorite(db: AsyncClient, word_id: int, is_favorite: bool):
    return await vocabulary_supabase.update_word_favorite_status(db, word_id, is_favorite)

async def get_all_favorite_words(db: AsyncClient, user_id: str):
    return await vocabulary_supabase.get_favorite_words(db, user_id)