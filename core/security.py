# 보안 관련 유틸리티(비밀번호 해싱, JWT 생성 및 검증)를 담당하는 파일
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from core import config

# 비밀번호 해싱을 위한 CryptContext 객체를 생성합니다. bcrypt 알고리즘을 사용합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password Hashing ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT Token ---
def create_access_token(data: dict):
    to_encode = data.copy() # 원본 데이터를 변경하지 않기 위해 복사합니다.
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

# 토큰을 디코딩하여 사용자 이름(payload의 'sub' 클레임)을 추출합니다.
def get_username_from_token(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None