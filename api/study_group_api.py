from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from supabase import AsyncClient

from core.database import get_db
from core.dependencies import get_current_user
from db import study_group_supabase
from models.challenge_model import ChallengeCreate, ChallengeResponse, ProgressLogRequest, ChallengeUpdate
from models.study_group_model import StudyGroupCreate, StudyGroupResponse, GroupMemberResponse, GroupMessageCreate, \
    GroupMessageResponse, JoinRequestResponse

router = APIRouter()

@router.post("/create", response_model=StudyGroupResponse)
async def create_study_group(
        group: StudyGroupCreate,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """학습 그룹 생성"""
    try:
        user_id = current_user.get('user_id')
        user_name = current_user.get('name') # 생성자 이름을 가져옵니다.

        group_data = await study_group_supabase.create_study_group(
            db=db,
            name=group.name,
            description=group.description,
            created_by=user_id,
            max_members=group.max_members,
            requires_approval=group.requires_approval
        )

        return StudyGroupResponse(
            id=group_data['id'],
            name=group_data['name'],
            description=group_data['description'],
            created_by=group_data['created_by'],
            creator_name=user_name, # 여기서 생성자 이름을 넣어줍니다.
            max_members=group_data['max_members'],
            member_count=1,
            is_member=True,
            is_owner=True,
            requires_approval=group_data['requires_approval'],
            created_at=group_data['created_at']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[StudyGroupResponse])
async def get_study_groups(
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """모든 학습 그룹 조회"""
    try:
        user_id = current_user.get('user_id')
        groups = await study_group_supabase.get_all_study_groups(db, user_id)
        return [StudyGroupResponse(**group) for group in groups]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{group_id}/join")
async def join_group(
        group_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """그룹 참여"""
    try:
        user_id = current_user.get('user_id')
        message = await study_group_supabase.join_study_group(db, group_id, user_id)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{group_id}/leave")
async def leave_group(
        group_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """그룹 탈퇴"""
    try:
        user_id = current_user.get('user_id')
        await study_group_supabase.leave_study_group(db, group_id, user_id)
        return {"message": "그룹에서 탈퇴했습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_group_members(
        group_id: int,
        # 그룹 멤버는 누구나 볼 수 있으므로 current_user 인증이 필수는 아닐 수 있습니다.
        # 만약 그룹 멤버만 보게 하려면 Depends(get_current_user)를 유지합니다.
        db: AsyncClient = Depends(get_db)
):
    """그룹 멤버 조회"""
    try:
        members = await study_group_supabase.get_group_members(db, group_id)
        return [GroupMemberResponse(**member) for member in members]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{group_id}")
async def delete_group(
        group_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """그룹 삭제 (owner 전용)"""
    try:
        user_id = current_user.get('user_id')
        await study_group_supabase.delete_study_group(db, group_id, user_id)
        return {"message": "그룹이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

# ==========================================================
# ▼▼▼ 여기가 정리된 올바른 메시지 관련 함수들입니다. ▼▼▼
# ==========================================================

@router.get("/{group_id}/messages", response_model=List[GroupMessageResponse])
async def get_group_messages(
        group_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """그룹 채팅 메시지 조회"""
    # 실제 프로덕션에서는 이 유저가 그룹 멤버인지 확인하는 로직이 추가되어야 합니다.
    try:
        messages = await study_group_supabase.get_group_messages(db, group_id)
        return [GroupMessageResponse(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{group_id}/messages", response_model=GroupMessageResponse)
async def post_group_message(
        group_id: int,
        message: GroupMessageCreate,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """그룹 채팅 메시지 작성"""
    try:
        user_id = current_user.get('user_id')
        user_name = current_user.get('name', 'Unknown')

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user token.")

        new_msg = await study_group_supabase.create_group_message(
            db=db,
            group_id=group_id,
            user_id=user_id,
            content=message.content
        )

        response_data = GroupMessageResponse(
            id=new_msg['id'],
            group_id=new_msg['group_id'],
            user_id=new_msg['user_id'],
            user_name=user_name,
            content=new_msg['content'],
            created_at=new_msg['created_at']
        )

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류 발생: {str(e)}")


# ==========================================================
# ▲▲▲ 메시지 관련 함수 끝 ▲▲▲
# ==========================================================

@router.get("/{group_id}/requests", response_model=List[JoinRequestResponse])
async def get_pending_requests(
        group_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """그룹 가입 요청 목록 조회 (그룹장 전용)"""
    try:
        owner_id = await study_group_supabase.get_group_owner(db, group_id)
        if owner_id != current_user.get('user_id'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

        requests = await study_group_supabase.get_join_requests(db, group_id)
        return [JoinRequestResponse(**req) for req in requests]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{group_id}/requests/{request_id}/approve")
async def approve_request(
        group_id: int,
        request_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """가입 요청 승인 (그룹장 전용)"""
    try:
        owner_id = await study_group_supabase.get_group_owner(db, group_id)
        if owner_id != current_user.get('user_id'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

        await study_group_supabase.process_join_request(db, request_id, 'approved')
        return {"message": "가입 요청을 승인했습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{group_id}/requests/{request_id}/reject")
async def reject_request(
        group_id: int,
        request_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """가입 요청 거절 (그룹장 전용)"""
    try:
        owner_id = await study_group_supabase.get_group_owner(db, group_id)
        if owner_id != current_user.get('user_id'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

        await study_group_supabase.process_join_request(db, request_id, 'rejected')
        return {"message": "가입 요청을 거절했습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{group_id}/challenges", response_model=ChallengeResponse)
async def create_challenge(
        group_id: int,
        challenge_in: ChallengeCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """그룹에 새로운 챌린지를 생성합니다 (그룹 멤버 전용).""" # 설명 수정
    user_id = current_user.get('user_id')
    user_name = current_user.get('name', 'Unknown')

    is_member = await study_group_supabase.is_user_group_member(db, group_id, user_id)
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹 멤버만 챌린지를 생성할 수 있습니다.")

    # DB에 챌린지 생성 (이하 로직은 동일)
    new_challenge_data = await study_group_supabase.create_challenge(db, group_id, user_id, challenge_in.model_dump())

    return ChallengeResponse(
        id=new_challenge_data['id'],
        group_id=new_challenge_data['group_id'],
        creator_id=new_challenge_data['created_by_user_id'],
        creator_name=user_name,
        title=new_challenge_data['title'],
        description=new_challenge_data['description'],
        challenge_type=new_challenge_data['challenge_type'],
        target_value=new_challenge_data['target_value'],
        user_current_value=0,
        is_completed=False,
        end_date=new_challenge_data['end_date'],
        is_active=new_challenge_data['is_active'],
        created_at=new_challenge_data['created_at']
    )


@router.get("/{group_id}/challenges", response_model=List[ChallengeResponse])
async def list_challenges(
        group_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """특정 스터디 그룹의 챌린지 목록을 조회합니다."""
    challenges = await study_group_supabase.get_challenges_by_group_id(db, group_id)

    response_data = []
    for c in challenges:
        response_data.append(ChallengeResponse(
            id=c['id'],
            group_id=c['group_id'],
            creator_id=c['created_by_user_id'],
            creator_name=c['creator_name'],
            title=c['title'],
            description=c['description'],
            challenge_type=c['challenge_type'],
            target_value=c['target_value'],
            user_current_value=c['user_current_value'],
            is_completed=c['is_completed'], # ▼▼▼ [5. 이 필드를 추가] ▼▼▼
            end_date=c['end_date'],
            is_active=c['is_active'],
            created_at=c['created_at']
        ))
    return response_data


@router.post("/challenges/log-progress", status_code=status.HTTP_204_NO_CONTENT)
async def log_challenge_progress(
        request: ProgressLogRequest,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """사용자의 학습 활동을 연관된 챌린지에 자동으로 기록합니다."""
    user_id = current_user.get('user_id')
    # challenge_supabase 모듈이 없으므로 study_group_supabase 사용
    await study_group_supabase.log_progress(db, user_id, request.log_type, request.value)

@router.put("/challenges/{challenge_id}", response_model=ChallengeResponse)
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

    # 수정 후 전체 데이터를 다시 조회해서 반환
    all_challenges = await study_group_supabase.get_challenges_by_group_id(db, updated_challenge['group_id'])
    for c in all_challenges:
        if c['id'] == challenge_id:
            return ChallengeResponse(**c)


@router.delete("/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
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