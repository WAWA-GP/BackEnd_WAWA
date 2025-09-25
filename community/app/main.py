# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import community, auth, user

app = FastAPI()

# ✅ 개발 단계: 테이블 자동 생성(Alembic 도입시 삭제)
Base.metadata.create_all(bind=engine)

# ✅ 라우터 등록
app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")
app.include_router(community.router, prefix="/community")