from fastapi import FastAPI
from app.routes import auth, oauth_google, user, admin  # ✅ admin, user 라우터도 import
from app.database import engine
from app import models

app = FastAPI()

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")         # ✅ 사용자 정보 수정 API
app.include_router(oauth_google.router)                 # ⬅️ 구글 OAuth 라우터
app.include_router(admin.router, prefix="/admin")       # ✅ 관리자 전용 라우터
