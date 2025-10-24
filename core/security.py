from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from core import config
import os
import logging
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # 보안 강화
    bcrypt__ident="2b"  # 최신 bcrypt 식별자 사용
)


# .env 파일의 SUPABASE_JWT_SECRET 값을 가져옵니다.
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = config.ALGORITHM

# --- Password Hashing ---
def hash_password(password: str) -> str:
    """비밀번호를 해싱합니다. 72바이트 제한 처리 포함"""
    try:
        # bcrypt는 72바이트까지만 처리 가능하므로 자르기
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
            logging.warning("비밀번호가 72바이트를 초과하여 잘렸습니다")

        hashed = pwd_context.hash(password)
        logging.info("비밀번호 해싱 성공")
        return hashed
    except Exception as e:
        logging.error(f"비밀번호 해싱 실패: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시를 비교합니다."""
    try:
        # 동일하게 72바이트 제한 적용
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
            logging.warning("검증할 비밀번호가 72바이트를 초과하여 잘렸습니다")

        result = pwd_context.verify(plain_password, hashed_password)
        logging.info(f"비밀번호 검증 완료 - 결과: {result}")
        return result
    except Exception as e:
        logging.error(f"비밀번호 검증 오류: {e}")
        return False
# --- JWT Token ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


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