from fastapi import FastAPI
from api import voca_api
from db.auth import get_current_user

app = FastAPI(
    title="학습 앱 API",
    description="API",
    version="1.0.0"
)

async def override_get_current_user():
    class MockUser:
        id = "790d0d81-e04f-4c36-add6-64982d7aa124"
    return MockUser()
app.dependency_overrides[get_current_user] = override_get_current_user
app.include_router(voca_api.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "학습 앱 API [테스트 모드]에 오신 것을 환영합니다! '/docs' 경로에서 API 문서를 확인하세요."}