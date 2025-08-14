from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.voca_models import VocaItem, AddVocaRequest, UpdateVocaRequest, SyncVocaRequest
from services import voca_service
from db.auth import get_current_user
from supabase_auth import User

router = APIRouter(
    prefix="/vocabulary",
    tags=["Vocabulary"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[VocaItem], summary="내 단어장 목록 조회")
async def get_my_vocabulary(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 단어장 전체 목록을 가져옵니다."""
    return voca_service.get_voca(str(current_user.id))

@router.post("/", status_code=status.HTTP_201_CREATED, summary="단어장에 새 단어 추가")
async def add_new_word(request: AddVocaRequest, current_user: User = Depends(get_current_user)):
    """'단어 사전'에서 단어를 검색하여 내 단어장에 추가합니다."""
    result = voca_service.add_voca(str(current_user.id), request.word, request.memo)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    return result

@router.put("/{word}/memo", summary="단어 메모 수정")
async def update_voca_memo(word: str, request: UpdateVocaRequest, current_user: User = Depends(get_current_user)):
    """단어장에 저장된 특정 단어의 메모를 수정합니다."""
    result = voca_service.update_voca(str(current_user.id), word, request.memo)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    return result

@router.delete("/{word}", status_code=status.HTTP_204_NO_CONTENT, summary="단어장에서 단어 삭제")
async def delete_a_word(word: str, current_user: User = Depends(get_current_user)):
    """단어장에서 특정 단어를 삭제합니다."""
    result = voca_service.delete_voca(str(current_user.id), word)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    return

@router.put("/sync", summary="로컬 단어장을 서버에 전체 동기화")
async def sync_full_vocabulary(request: SyncVocaRequest, current_user: User = Depends(get_current_user)):
    """
    클라이언트(로컬)의 단어장 전체 목록을 서버에 덮어쓰기하여 동기화합니다.
    오프라인 상태에서 변경된 내용을 한 번에 반영할 때 사용합니다.
    """
    result = voca_service.sync_voca(str(current_user.id), request.voca_data)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return result