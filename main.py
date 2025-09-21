# FastAPI 애플리케이션의 통합된 메인 파일
from fastapi import FastAPI
from dotenv import load_dotenv

from api import (
    auth_api, user_api, admin_api, notice_api,
    faq_api, level_test_api, attendance_api, plan_api, statistics_api
)

from models import table_models
from core.database import engine

load_dotenv()

# SQLAlchemy 모델을 기반으로 데이터베이스에 모든 테이블을 생성합니다. (기존 프로젝트의 필수 기능 유지)
models.Base.metadata.create_all(bind=engine)

# FastAPI 앱 인스턴스를 생성.
app = FastAPI(
    title="통합 모듈 API",
    description="통합 모듈 API",
    version="1.0.0"
)

# 1. 학습 계획 생성 API
app.include_router(
    plan_api.router,
    prefix="/api/plans", # 새로운 main.py의 prefix 적용
    tags=["Learning Plans"]
)
# 2. 학습 통계 조회 API
app.include_router(
    statistics_api.router,
    prefix="/api/statistics", # 새로운 main.py의 prefix 적용
    tags=["Learning Statistics"]
)

# 3. 로그인/인증 API (기존 auth_api를 사용, prefix와 태그는 새로운 main.py의 형식에 맞춤)
app.include_router(
    auth_api.router,
    prefix="/auth",
    tags=["Auth"]
)

# 4. 사용자 프로필 API
app.include_router(
    user_api.router,
    prefix="/api/user",
    tags=["User"]
)

# 5. 관리자 API
app.include_router(
    admin_api.router,
    prefix="/api/admin",
    tags=["Admin"]
)

# 6. 공지사항 API
app.include_router(
    notice_api.router,
    prefix="/api/notices",
    tags=["Notices"]
)

# 7. FAQ API
app.include_router(
    faq_api.router,
    prefix="/api/faqs",
    tags=["FAQs"]
)

# 8. 레벨 테스트 API
app.include_router(
    level_test_api.router,
    prefix="/api/level-test",
    tags=["Level Test"]
)

# 9. 출석 체크 API
app.include_router(
    attendance_api.router,
    prefix="/api/attendance",
    tags=["Attendance"]
)

# 서버 정상 동작 확인
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "서버 정상 동작중"}