from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import auth, oauth_google, user, admin, level_test
from app.database import engine
from app import models
from app.utils.exception_handlers import (
    http_exception_handler,
    validation_exception_handler
)

app = FastAPI()

# ✅ 예외 핸들러 등록
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")
app.include_router(oauth_google.router)
app.include_router(admin.router, prefix="/admin")
app.include_router(level_test.router)