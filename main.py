from fastapi import FastAPI
from dotenv import load_dotenv
from api import plan_api, statistics_api, login_api, admin_api, community_api, notification_api, attendance_api, auth_api, faq_api, leveltest_api, notice_api, user_api
from services.performance_monitor import performance_monitor
from profiler_middleware import PyInstrumentProfilerMiddleware
from supabase import create_client, AsyncClient
import logging
from services import notification_service

# .env 파일에서 환경 변수 로드
load_dotenv()

# FastAPI 앱 초기화
app = FastAPI(
    title="통합 모듈 API",
    description="로그인, 사용자별 맞춤 학습 계획 생성, 학습 통계 조회 API",
    version="1.0.0"
)

# --- API 라우터 ---
# 1. 학습 계획 성생 API
app.include_router(
    plan_api.router,
    prefix="/api/plans",
    tags=["Learning Plans"]
)
# 2. 학습 통계 조회 API
app.include_router(
    statistics_api.router,
    prefix="/api/statistics",
    tags=["Learning Statistics"]
)

# 3. 로그인 API
app.include_router(
    login_api.router,
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
    leveltest_api.router,
    prefix="/api/level-test",
    tags=["Level Test"]
)

# 9. 출석 체크 API
app.include_router(
    attendance_api.router,
    prefix="/api/attendance",
    tags=["Attendance"]
)

# 10. 푸시 알림 API
app.include_router(
    notification_api.router,
    prefix="/api/notifications",
    tags=["User Notifications"]
)

# 11. 커뮤니티 API
app.include_router(
    community_api.router,
    prefix="/api/community",
    tags=["Community"]
)

# 서버 정상 동작 확인
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "서버 정상 동작중"}

@app.on_event("shutdown")
def shutdown_event():
    print("👋 서버가 종료됩니다. 성능 리포트를 생성합니다...")
    performance_monitor.generate_report()
