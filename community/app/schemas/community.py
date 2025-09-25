# app/schemas/community.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ====== 기본 스키마 ======
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


class PostResponse(PostBase):
    id: int
    user_id: int
    is_deleted: bool
    created_at: datetime

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    name: str


class TagResponse(TagBase):
    id: int

    class Config:
        orm_mode = True


class ReportBase(BaseModel):
    reason: str


class ReportCreate(ReportBase):
    post_id: Optional[int]
    comment_id: Optional[int]


class ReportResponse(ReportBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True