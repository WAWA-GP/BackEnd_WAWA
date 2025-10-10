import os
from dotenv import load_dotenv

# .env 파일에서 환경변수를 로드합니다.
load_dotenv()

# JWT 설정
SECRET_KEY = "a9cbf27e75b668b629aa083b504f00a23e27c5e2d1e480430b1019a793d164b2"
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Google OAuth 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")