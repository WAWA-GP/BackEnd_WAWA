# services/community_service.py

from supabase import AsyncClient
from db import community_supabase
from models import community_model

# ====== 게시글 (Post) ======
async def create_new_post(db: AsyncClient, post: community_model.PostCreate, user_id: str):
    return await community_supabase.create_post(db, post, user_id)

async def get_all_posts(db: AsyncClient, category: str):
    return await community_supabase.get_all_posts(db, category)

async def get_post_by_id(db: AsyncClient, post_id: int):
    return await community_supabase.get_post_by_id(db, post_id)

async def update_existing_post(db: AsyncClient, post_id: int, post_update: community_model.PostUpdate, current_user: dict):
    post = await community_supabase.get_post_by_id(db, post_id)
    if not post:
        return None # 게시글 없음

    # 권한 확인: 관리자이거나 본인 글일 경우에만 수정 가능
    if not current_user.get('is_admin') and post.get('user_id') != current_user.get('user_id'):
        return "unauthorized" # 권한 없음

    return await community_supabase.update_post(db, post_id, post_update)

async def delete_existing_post(db: AsyncClient, post_id: int, current_user: dict):
    post = await community_supabase.get_post_by_id(db, post_id)
    if not post:
        return None # 게시글 없음

    # 권한 확인: 관리자이거나 본인 글일 경우에만 삭제 가능
    if not current_user.get('is_admin') and post.get('user_id') != current_user.get('user_id'):
        return "unauthorized" # 권한 없음

    return await community_supabase.delete_post(db, post_id)

# ====== 댓글 (Comment) ======
async def create_new_comment(db: AsyncClient, comment: community_model.CommentCreate, post_id: int, user_id: str):
    return await community_supabase.create_comment(db, comment, post_id, user_id)

async def get_all_comments_for_post(db: AsyncClient, post_id: int):
    return await community_supabase.get_comments_by_post_id(db, post_id)

# ====== 신고 (Report) ======
async def create_new_report(db: AsyncClient, report: community_model.ReportCreate, user_id: str):
    return await community_supabase.create_report(db, report, user_id)

async def get_all_reports(db: AsyncClient):
    return await community_supabase.get_all_reports(db)
