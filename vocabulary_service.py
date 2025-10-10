from supabase import AsyncClient
from db import vocabulary_supabase
from models import vocabulary_model
from fastapi import HTTPException

# --- Wordbook ---
async def create_new_wordbook(db: AsyncClient, name: str, user_id: str):
    return await vocabulary_supabase.create_wordbook(db, name, user_id)

async def get_user_wordbooks(db: AsyncClient, user_id: str):
    wordbooks = await vocabulary_supabase.get_wordbooks_by_user(db, user_id)
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
        raise HTTPException(status_code=404, detail="요청한 단어장을 찾을 수 없습니다.")
    wordbook_data['words'] = wordbook_data.get('user_words', [])
    return vocabulary_model.WordbookDetailResponse.model_validate(wordbook_data)

async def toggle_word_memorized(db: AsyncClient, word_id: int, is_memorized: bool):
    return await vocabulary_supabase.update_word_status(db, word_id, is_memorized)

async def remove_word_from_wordbook(db: AsyncClient, word_id: int):
    deleted_word = await vocabulary_supabase.delete_word(db, word_id)
    if not deleted_word:
        raise HTTPException(status_code=404, detail="삭제할 단어를 찾을 수 없습니다.")
    return deleted_word

async def add_new_words_batch(db: AsyncClient, words_in: vocabulary_model.UserWordBatchCreate, wordbook_id: int):
    words_to_insert = [
        {**word.model_dump(), "wordbook_id": wordbook_id}
        for word in words_in.words
    ]
    return await vocabulary_supabase.add_words_to_wordbook_batch(db, words_to_insert)

async def delete_user_wordbook(db: AsyncClient, wordbook_id: int, user_id: str):
    deleted_wordbook = await vocabulary_supabase.delete_wordbook(db, wordbook_id, user_id)
    if not deleted_wordbook:
        raise HTTPException(status_code=404, detail="단어장을 삭제할 수 없거나 찾을 수 없습니다.")
    return deleted_wordbook

async def toggle_word_favorite(db: AsyncClient, word_id: int, is_favorite: bool):
    return await vocabulary_supabase.update_word_favorite_status(db, word_id, is_favorite)

async def get_all_favorite_words(db: AsyncClient, user_id: str):
    return await vocabulary_supabase.get_favorite_words(db, user_id)

async def get_word_stats(db: AsyncClient, user_id: str):
    return await vocabulary_supabase.get_word_stats_by_user(db, user_id)

async def get_all_words(db: AsyncClient, user_id: str, status: str | None):
    return await vocabulary_supabase.get_all_words_by_user(db, user_id, status)

# --- 검색 및 상세 조회 ---
async def search_user_words(db: AsyncClient, user_id: str, query: str):
    return await vocabulary_supabase.search_user_words(db, user_id, query)

async def get_word_detail(db: AsyncClient, user_id: str, word_id: int):
    return await vocabulary_supabase.get_user_word_detail(db, user_id, word_id)