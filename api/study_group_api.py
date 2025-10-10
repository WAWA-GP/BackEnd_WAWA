<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, Depends, status
from core.dependencies import get_current_user
from core.database import get_db
from supabase import AsyncClient
from models.study_group_model import StudyGroupCreate, StudyGroupResponse, GroupMemberResponse, GroupMessageCreate, GroupMessageResponse, JoinRequestResponse
=======
from fastapi import APIRouter, HTTPException, Depends
from core.dependencies import get_current_user
from core.database import get_db
from supabase import AsyncClient
from models.study_group_model import StudyGroupCreate, StudyGroupResponse, GroupMemberResponse
>>>>>>> origin/master
from db import study_group_supabase
from typing import List

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
<<<<<<< HEAD
        user_name = current_user.get('name') # 생성자 이름을 가져옵니다.
=======
>>>>>>> origin/master

        group_data = await study_group_supabase.create_study_group(
            db=db,
            name=group.name,
            description=group.description,
            created_by=user_id,
<<<<<<< HEAD
            max_members=group.max_members,
            requires_approval=group.requires_approval
=======
            max_members=group.max_members
>>>>>>> origin/master
        )

        return StudyGroupResponse(
            id=group_data['id'],
            name=group_data['name'],
            description=group_data['description'],
            created_by=group_data['created_by'],
<<<<<<< HEAD
            creator_name=user_name, # 여기서 생성자 이름을 넣어줍니다.
=======
            creator_name=current_user.get('name'),
>>>>>>> origin/master
            max_members=group_data['max_members'],
            member_count=1,
            is_member=True,
            is_owner=True,
<<<<<<< HEAD
            requires_approval=group_data['requires_approval'],
=======
>>>>>>> origin/master
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
<<<<<<< HEAD
=======

>>>>>>> origin/master
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
<<<<<<< HEAD
        message = await study_group_supabase.join_study_group(db, group_id, user_id)
        return {"message": message}
=======
        await study_group_supabase.join_study_group(db, group_id, user_id)
        return {"message": "그룹에 참여했습니다."}
>>>>>>> origin/master
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
<<<<<<< HEAD
        # 그룹 멤버는 누구나 볼 수 있으므로 current_user 인증이 필수는 아닐 수 있습니다.
        # 만약 그룹 멤버만 보게 하려면 Depends(get_current_user)를 유지합니다.
=======
        current_user: dict = Depends(get_current_user),
>>>>>>> origin/master
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
<<<<<<< HEAD
    """그룹 삭제 (owner 전용)"""
=======
    """그룹 삭제"""
>>>>>>> origin/master
    try:
        user_id = current_user.get('user_id')
        await study_group_supabase.delete_study_group(db, group_id, user_id)
        return {"message": "그룹이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
<<<<<<< HEAD

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
    # 실제 프로덕션에서는 이 유저가 그룹 멤버인지 확인하는 로직이 추가되어야 합니다.
    try:
        user_id = current_user.get('user_id')
        user_name = current_user.get('name', 'Unknown')

        new_msg = await study_group_supabase.create_group_message(db, group_id, user_id, message.content)

        # user_name을 현재 로그인한 사용자 정보에서 가져와 응답 모델을 만듭니다.
        return GroupMessageResponse(
            id=new_msg['id'],
            group_id=new_msg['group_id'],
            user_id=new_msg['user_id'],
            user_name=user_name,
            content=new_msg['content'],
            created_at=new_msg['created_at']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
=======
>>>>>>> origin/master
