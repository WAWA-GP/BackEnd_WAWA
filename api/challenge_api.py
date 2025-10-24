# api/challenge_api.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient

from core.database import get_db
from core.dependencies import get_current_user
from db import study_group_supabase, user_crud
from models.challenge_model import ChallengeUpdate, ChallengeResponse, ProgressLogRequest, ChallengeCreate

router = APIRouter()

@router.post("/log-progress", status_code=status.HTTP_204_NO_CONTENT)
async def log_challenge_progress(
        request: ProgressLogRequest,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """사용자의 학습 활동을 연관된 챌린지에 자동으로 기록합니다."""
    user_id = current_user.get('user_id')
    await study_group_supabase.log_progress(db, user_id, request.log_type, request.value)
# ▲▲▲ 위치 이동 완료 ▲▲▲


@router.put("/{challenge_id}", response_model=ChallengeResponse)
async def update_challenge(
        challenge_id: int,
        challenge_in: ChallengeUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """챌린지를 수정합니다 (생성자 전용)."""
    user_id = current_user.get('user_id')

    challenge = await study_group_supabase.get_challenge_by_id(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="챌린지를 찾을 수 없습니다.")
    if challenge['created_by_user_id'] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="수정 권한이 없습니다.")

    # ▼▼▼ [수정] 이 아랫부분을 수정합니다. ▼▼▼

    # 1. 챌린지 내용 업데이트
    await study_group_supabase.update_challenge(db, challenge_id, challenge_in.model_dump(exclude_unset=True))

    # 2. 최신 챌린지 전체 정보를 다시 조회하여 반환
    all_challenges = await study_group_supabase.get_challenges_by_group_id(db, challenge['group_id'], user_id)
    for c in all_challenges:
        if c['id'] == challenge_id:
            return c # get_challenges_by_group_id가 반환하는 형식은 이미 ChallengeResponse와 호환됩니다.

    # 만약 위 루프에서 못찾는 예외적인 경우
    raise HTTPException(status_code=404, detail="업데이트된 챌린지 정보를 반환할 수 없습니다.")

@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge(
        challenge_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """챌린지를 삭제합니다 (생성자 전용)."""
    user_id = current_user.get('user_id')

    challenge = await study_group_supabase.get_challenge_by_id(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="챌린지를 찾을 수 없습니다.")
    if challenge['created_by_user_id'] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="삭제 권한이 없습니다.")

    await study_group_supabase.delete_challenge(db, challenge_id)

@router.post("/study-groups/{group_id}/challenges", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
async def create_challenge(
        group_id: int,
        challenge_in: ChallengeCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """그룹에 새로운 챌린지를 생성합니다 (그룹 멤버 누구나 가능)."""
    user_id = current_user.get('user_id')

    # 그룹 멤버인지 확인
    is_member = await study_group_supabase.is_user_group_member(db, group_id, user_id)
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹 멤버만 챌린지를 생성할 수 있습니다.")

    # study_group_supabase의 create_challenge 함수를 호출
    new_challenge = await study_group_supabase.create_challenge(db, group_id, user_id, challenge_in)

    # 응답 모델에 맞게 데이터를 재구성하여 반환
    user_info = await user_crud.get_user(db, user_id)
    creator_name = user_info.get('name', 'Unknown') if user_info else 'Unknown'

    return ChallengeResponse(
        id=new_challenge['id'],
        group_id=new_challenge['group_id'],
        creator_id=new_challenge['created_by_user_id'],
        creator_name=creator_name,
        title=new_challenge['title'],
        description=new_challenge['description'],
        end_date=new_challenge['end_date'],
        created_at=new_challenge['created_at'],
        participants=[],
        user_has_completed=False
    )


@router.get("/study-groups/{group_id}/challenges", response_model=List[ChallengeResponse])
async def list_challenges(
        group_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """특정 스터디 그룹의 챌린지 목록을 조회합니다."""
    user_id = current_user.get('user_id')
    # study_group_supabase의 함수를 호출하도록 변경
    challenges = await study_group_supabase.get_challenges_by_group_id(db, group_id, user_id)
    return challenges