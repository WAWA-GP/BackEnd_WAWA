from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from core import config
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# .env 파일의 SUPABASE_JWT_SECRET 값을 가져옵니다.
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = config.ALGORITHM

# --- Password Hashing ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT Token ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

# --- JWT Token ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # ▼▼▼ [수정] JWT_SECRET 변수를 사용합니다. ▼▼▼
    return jwt.encode(to_encode, JWT_SECRET, algorithm=config.ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    # ▼▼▼ [수정] JWT_SECRET 변수를 사용합니다. ▼▼▼
    return jwt.encode(to_encode, JWT_SECRET, algorithm=config.ALGORITHM)


def get_username_from_token(token: str):
    try:
        # 👈 jose.jwt.decode 사용 확인
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM],
            audience='authenticated' # 👈 audience 옵션도 여기에 포함
        )
        return payload.get("email")
    except JWTError:
        return None
