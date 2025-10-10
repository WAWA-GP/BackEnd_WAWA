from fastapi import APIRouter, HTTPException, Depends
from core.dependencies import get_current_user
from core.database import get_db
from supabase import AsyncClient
from models.study_group_model import StudyGroupCreate, StudyGroupResponse, GroupMemberResponse
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

        group_data = await study_group_supabase.create_study_group(
            db=db,
            name=group.name,
            description=group.description,
            created_by=user_id,
            max_members=group.max_members
        )

        return StudyGroupResponse(
            id=group_data['id'],
            name=group_data['name'],
            description=group_data['description'],
            created_by=group_data['created_by'],
            creator_name=current_user.get('name'),
            max_members=group_data['max_members'],
            member_count=1,
            is_member=True,
            is_owner=True,
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
        await study_group_supabase.join_study_group(db, group_id, user_id)
        return {"message": "그룹에 참여했습니다."}
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
        current_user: dict = Depends(get_current_user),
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
    """그룹 삭제"""
    try:
        user_id = current_user.get('user_id')
        await study_group_supabase.delete_study_group(db, group_id, user_id)
        return {"message": "그룹이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
