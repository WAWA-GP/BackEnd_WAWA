# api/community_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from typing import List

from core.database import get_db
from core.dependencies import get_current_user, get_current_admin
from services import community_service
from models import community_model

router = APIRouter()

# ====== 게시글 (Post) ======
@router.post("/posts", response_model=community_model.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
        post_in: community_model.PostCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    return await community_service.create_new_post(db, post_in, user_id)

@router.get("/posts", response_model=List[community_model.PostResponse])
async def list_posts(category: str, db: AsyncClient = Depends(get_db)):
    return await community_service.get_all_posts(db, category)

@router.get("/posts/{post_id}", response_model=community_model.PostResponse)
async def get_post(post_id: int, db: AsyncClient = Depends(get_db)):
    post = await community_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

@router.put("/posts/{post_id}", response_model=community_model.PostResponse)
async def update_post(
        post_id: int,
        post_in: community_model.PostUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    result = await community_service.update_existing_post(db, post_id, post_in, current_user)
    if result is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if result == "unauthorized":
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")
    return result

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    result = await community_service.delete_existing_post(db, post_id, current_user)
    if result is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if result == "unauthorized":
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")


# ====== 댓글 (Comment) ======
@router.post("/posts/{post_id}/comments", response_model=community_model.CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        post_id: int,
        comment_in: community_model.CommentCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    new_comment = await community_service.create_new_comment(db, comment_in, post_id, user_id)
    if not new_comment:
        raise HTTPException(status_code=400, detail="댓글 생성에 실패했습니다.")
    return new_comment

@router.get("/posts/{post_id}/comments", response_model=List[community_model.CommentResponse])
async def list_comments(post_id: int, db: AsyncClient = Depends(get_db)):
    return await community_service.get_all_comments_for_post(db, post_id)

# ▼▼▼ [신규] 댓글 수정을 위한 API 엔드포인트 ▼▼▼
@router.put("/comments/{comment_id}", response_model=community_model.CommentResponse)
async def update_comment(
        comment_id: int,
        comment_in: community_model.CommentUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    result = await community_service.update_existing_comment(db, comment_id, comment_in, current_user)
    if result is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if result == "unauthorized":
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")
    return result

# ▼▼▼ [신규] 댓글 삭제를 위한 API 엔드포인트 ▼▼▼
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: int,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    result = await community_service.delete_existing_comment(db, comment_id, current_user)
    if result is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if result == "unauthorized":
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")


# ====== 신고 (Report) ======
@router.post("/reports", response_model=community_model.ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
        report_in: community_model.ReportCreate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    return await community_service.create_new_report(db, report_in, user_id)

@router.get("/reports", response_model=List[community_model.ReportResponse])
async def list_reports(
        db: AsyncClient = Depends(get_db),
        admin: dict = Depends(get_current_admin)
):
    return await community_service.get_all_reports(db)