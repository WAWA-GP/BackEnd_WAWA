from pydantic import BaseModel, Field
from typing import List, Optional

class VocaItem(BaseModel):
    word: str = Field(..., description="단어 (스펠링)")
    pronunciation: Optional[str] = Field(None, description="발음")
    pos: str = Field(..., description="품사")
    meaning: str = Field(..., description="의미")
    memo: str = Field("", description="사용자 메모")

    class Config:
        from_attributes = True

class AddVocaRequest(BaseModel):
    word: str = Field(..., description="추가할 단어")
    memo: str = Field("", description="추가할 메모")

class UpdateVocaRequest(BaseModel):
    memo: str = Field(..., description="새로운 메모 내용")

class SyncVocaRequest(BaseModel):
    voca_data: List[VocaItem] = Field(..., description="동기화할 단어장 전체 목록")