from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth
from app.utils.jwt_utils import create_access_token, decode_access_token

load_dotenv()  # .env 로드

router = APIRouter()

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get("/auth/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    # 여기에 DB 저장 or JWT 발급 등을 추가할 수 있음
    return JSONResponse(content={"user": user_info})
