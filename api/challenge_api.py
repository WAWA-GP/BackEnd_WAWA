# api/challenge_api.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient

from core.database import get_db
from core.dependencies import get_current_user
from db import challenge_supabase, study_group_supabase
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

    updated_challenge = await study_group_supabase.update_challenge(db, challenge_id, challenge_in.model_dump(exclude_unset=True))

    all_challenges = await study_group_supabase.get_challenges_by_group_id(db, updated_challenge['group_id'])
    for c in all_challenges:
        if c['id'] == challenge_id:
            return ChallengeResponse(
                id=c['id'], group_id=c['group_id'], creator_id=c['created_by_user_id'],
                creator_name=c['creator_name'], title=c['title'], description=c['description'],
                challenge_type=c['challenge_type'], target_value=c['target_value'],
                user_current_value=c['user_current_value'], end_date=c['end_date'],
                is_active=c['is_active'], created_at=c['created_at']
            )

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

@router.post("/study-groups/{group_id}/challenges", response_model=ChallengeResponse)
async def create_challenge(
        group_id: int,
        challenge_in: ChallengeCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """그룹에 새로운 챌린지를 생성합니다 (그룹장 전용)."""
    user_id = current_user.get('user_id')

    # 그룹장인지 권한 확인
    owner_id = await study_group_supabase.get_group_owner(db, group_id)
    if owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="챌린지를 생성할 권한이 없습니다.")

    new_challenge = await challenge_supabase.create_challenge(db, group_id, user_id, challenge_in.model_dump())
    return ChallengeResponse(group_current_value=0, **new_challenge)


@router.get("/study-groups/{group_id}/challenges", response_model=List[ChallengeResponse])
async def list_challenges(
        group_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user) # 그룹 멤버인지 확인하기 위해 필요
):
    """특정 스터디 그룹의 챌린지 목록을 조회합니다."""
    challenges = await challenge_supabase.get_challenges_by_group_id(db, group_id)
    return [ChallengeResponse(**c) for c in challenges]