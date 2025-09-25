# db/community_supabase.py

from supabase import AsyncClient
from models import community_model

# ====== 게시글 (Post) ======
async def create_post(db: AsyncClient, post: community_model.PostCreate, user_id: str):
    post_data = post.model_dump()
    post_data['user_id'] = user_id
    response = await db.table("posts").insert(post_data).execute()
    return response.data[0] if response.data else None

async def get_all_posts(db: AsyncClient, category: str):
    response = await db.table("posts").select("*, user_account(name)").eq("is_deleted", False).eq("category", category).order("created_at", desc=True).execute()
    return response.data

async def get_post_by_id(db: AsyncClient, post_id: int):
    response = await db.table("posts").select("*, user_account(name)").eq("id", post_id).eq("is_deleted", False).maybe_single().execute()
    return response.data

async def update_post(db: AsyncClient, post_id: int, post_update: community_model.PostUpdate):
    update_data = post_update.model_dump(exclude_unset=True)
    response = await db.table("posts").update(update_data).eq("id", post_id).execute()
    return response.data[0] if response.data else None

async def delete_post(db: AsyncClient, post_id: int):
    # 실제 삭제 대신 is_deleted 플래그를 True로 업데이트 (논리적 삭제)
    response = await db.table("posts").update({"is_deleted": True}).eq("id", post_id).execute()
    return response.data[0] if response.data else None

# ====== 댓글 (Comment) ======
async def create_comment(db: AsyncClient, comment: community_model.CommentCreate, post_id: int, user_id: str):
    comment_data = comment.model_dump()
    comment_data['post_id'] = post_id
    comment_data['user_id'] = user_id
    response = await db.table("comments").insert(comment_data).execute()
    return response.data[0] if response.data else None

async def get_comments_by_post_id(db: AsyncClient, post_id: int):
    response = await db.table("comments").select("*, user_account(name)").eq("post_id", post_id).order("created_at", desc=False).execute()
    return response.data

# ====== 신고 (Report) ======
async def create_report(db: AsyncClient, report: community_model.ReportCreate, user_id: str):
    report_data = report.model_dump()
    report_data['user_id'] = user_id
    response = await db.table("reports").insert(report_data).execute()
    return response.data[0] if response.data else None

async def get_all_reports(db: AsyncClient):
    response = await db.table("reports").select("*").execute()
    return response.data
