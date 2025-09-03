import os
from fastapi import FastAPI
from dotenv import load_dotenv
from api.plan_api import router as plan_router

load_dotenv()

app = FastAPI(
    title="맞춤 학습 계획 생성 API",
    description="맞춤 학습 계획 생성",
    version="1.0.0"
)

app.include_router(plan_router, prefix="/api/plans", tags=["Learning Plans"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "서버 정상 실행중"}

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Supabase 설정 오류")
