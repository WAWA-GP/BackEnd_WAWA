# app/routers/community.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.community import Post, Comment, Report
from app.schemas.community import (
    PostCreate, PostResponse, PostUpdate,
    CommentCreate, CommentResponse,
    ReportCreate, ReportResponse
)
from app.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.utils.exceptions import http_error


router = APIRouter(prefix="/community", tags=["Community"])


# ====== 게시글 ======
@router.post("/posts", response_model=PostResponse)
def create_post(
        post_in: PostCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post = Post(title=post_in.title, content=post_in.content, user_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/posts", response_model=List[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.is_deleted == False).all()


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
    if not post:
        raise http_error(404, "게시글을 찾을 수 없습니다")
    return post


@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
        post_id: int,
        post_in: PostUpdate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
    if not post:
        raise http_error(404, "게시글을 찾을 수 없습니다")
    if post.user_id != user.id and not user.is_admin:
        raise http_error(403, "수정 권한이 없습니다")

    if post_in.title:
        post.title = post_in.title
    if post_in.content:
        post.content = post_in.content
    db.commit()
    db.refresh(post)
    return post


@router.delete("/posts/{post_id}")
def delete_post(
        post_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise http_error(404, "게시글을 찾을 수 없습니다")
    if not user.is_admin and post.user_id != user.id:
        raise http_error(403, "삭제 권한이 없습니다")

    post.is_deleted = True
    db.commit()
    return {"msg": "삭제되었습니다"}


# ====== 댓글 ======
@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
def create_comment(
        post_id: int,
        comment_in: CommentCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    comment = Comment(content=comment_in.content, user_id=user.id, post_id=post_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.post_id == post_id).all()


# ====== 신고 ======
@router.post("/reports", response_model=ReportResponse)
def create_report(
        report_in: ReportCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    report = Report(
        reason=report_in.reason,
        post_id=report_in.post_id,
        comment_id=report_in.comment_id,
        user_id=user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports", response_model=List[ReportResponse])
def list_reports(
        db: Session = Depends(get_db),
        admin: User = Depends(get_current_admin),
):
    return db.query(Report).all()