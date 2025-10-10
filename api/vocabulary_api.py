# api/vocabulary_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_user
from db import vocabulary_supabase
from services import vocabulary_service
from models import vocabulary_model

router = APIRouter()

# --- 단어장(Wordbook) 관련 API ---

@router.post("/wordbooks", response_model=vocabulary_model.WordbookResponse, status_code=status.HTTP_201_CREATED)
async def create_wordbook(
        wordbook_in: vocabulary_model.WordbookCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    return await vocabulary_service.create_new_wordbook(db, wordbook_in.name, user_id)

@router.get("/wordbooks", response_model=List[vocabulary_model.WordbookResponse])
async def get_my_wordbooks(
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    return await vocabulary_service.get_user_wordbooks(db, user_id)

@router.get("/wordbooks/{wordbook_id}", response_model=vocabulary_model.WordbookDetailResponse)
async def get_wordbook_details(
        wordbook_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    wordbook = await vocabulary_service.get_full_wordbook(db, wordbook_id, user_id)
    if not wordbook:
        raise HTTPException(status_code=404, detail="단어장을 찾을 수 없습니다.")
    return wordbook

# --- 단어(UserWord) 관련 API ---

@router.post("/wordbooks/{wordbook_id}/words", response_model=vocabulary_model.UserWordResponse, status_code=status.HTTP_201_CREATED)
async def add_word(
        wordbook_id: int,
        word_in: vocabulary_model.UserWordCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # TODO: 사용자가 해당 단어장의 소유자인지 확인하는 로직 추가
    return await vocabulary_service.add_new_word(db, word_in, wordbook_id)

@router.put("/words/{word_id}", response_model=vocabulary_model.UserWordResponse)
async def update_word_content(
        word_id: int,
        word_in: vocabulary_model.UserWordContentUpdate, # 1번에서 만든 모델 사용
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # TODO: 사용자가 해당 단어의 소유자인지 확인하는 로직 추가
    updated_word = await vocabulary_service.update_word_content(db, word_id, word_in)
    if not updated_word:
        raise HTTPException(status_code=404, detail="수정할 단어를 찾을 수 없습니다.")
    return updated_word

@router.patch("/words/{word_id}", response_model=vocabulary_model.UserWordResponse)
async def update_word(
        word_id: int,
        word_update: vocabulary_model.UserWordUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # TODO: 사용자가 해당 단어의 소유자인지 확인하는 로직 추가
    return await vocabulary_service.toggle_word_memorized(db, word_id, word_update.is_memorized)

@router.delete("/words/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word(
        word_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # TODO: 사용자가 해당 단어의 소유자인지 확인하는 로직 추가
    await vocabulary_service.remove_word_from_wordbook(db, word_id)
    return

@router.post("/wordbooks/{wordbook_id}/words/batch", status_code=status.HTTP_201_CREATED)
async def add_words_batch(
        wordbook_id: int,
        words_in: vocabulary_model.UserWordBatchCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # TODO: 사용자가 해당 단어장의 소유자인지 확인하는 로직 추가
    await vocabulary_service.add_new_words_batch(db, words_in, wordbook_id)
    return {"message": f"{len(words_in.words)} words added successfully"}

@router.delete("/wordbooks/{wordbook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wordbook(
        wordbook_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    result = await vocabulary_service.delete_user_wordbook(db, wordbook_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="삭제할 단어장을 찾을 수 없거나 권한이 없습니다.")
    return

@router.patch("/words/{word_id}/favorite", response_model=vocabulary_model.UserWordResponse)
async def update_word_favorite(
        word_id: int,
        is_favorite: bool, # 간단한 토글을 위해 body 대신 query parameter 사용
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # TODO: 사용자가 해당 단어의 소유자인지 확인하는 로직 추가
    word = await vocabulary_service.toggle_word_favorite(db, word_id, is_favorite)
    if not word:
        raise HTTPException(status_code=404, detail="단어를 찾을 수 없습니다.")
    return word

@router.get("/favorites", response_model=List[vocabulary_model.UserWordResponse])
async def get_favorites(
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    return await vocabulary_service.get_all_favorite_words(db, user_id)

@router.get("/stats", response_model=dict)
async def get_stats(
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    # 서비스 계층을 거치지 않고 직접 호출 (또는 서비스에 추가)
    stats = await vocabulary_supabase.get_word_stats_by_user(db, user_id)
    return stats

@router.get("/words", response_model=List[vocabulary_model.UserWordResponse])
async def get_all_words(
        status: Optional[str] = None, # 'memorized', 'not_memorized'
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    # 서비스 계층을 거치지 않고 직접 호출 (또는 서비스에 추가)
    return await vocabulary_supabase.get_all_words_by_user(db, user_id, status)

@router.get("/analysis", response_model=dict)
async def get_vocabulary_analysis(
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    stats = await vocabulary_supabase.get_word_stats_by_user(db, user_id)
    if not stats:
        return {
            "total_count": 0,
            "memorized_count": 0,
            "not_memorized_count": 0,
            "review_accuracy": 0.0,
        }
<<<<<<< HEAD
    return stats
=======
    return stats
>>>>>>> origin/master
