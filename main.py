from fastapi import FastAPI
from dotenv import load_dotenv
from api import plan_api, statistics_api, login_api

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

# 서버 정상 동작 확인
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "서버 정상 동작중"}

