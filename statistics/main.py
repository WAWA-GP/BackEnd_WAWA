import os
from fastapi import FastAPI
from dotenv import load_dotenv
from api import statistics_api

load_dotenv()
app = FastAPI(
    title="학습 통계 API",
    description="학습 통계",
    version="1.0.0"
)

app.include_router(statistics_api.router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "서버 정상 실행중"}


supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Supabase 설정 오류")
