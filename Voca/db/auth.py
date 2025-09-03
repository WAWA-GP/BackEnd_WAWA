from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from db.supabase_client import supabase

# HTTP "Authorization: Bearer <token>" 헤더를 해석하기 위한 객체를 생성합니다.
bearer_scheme = HTTPBearer()

# 비동기 함수로 'get_current_user'를 정의합니다. 이 함수 자체가 하나의 '의존성(Dependency)'으로 사용됩니다.
async def get_current_user(token: str = Depends(bearer_scheme)):
    """
    API 요청 헤더의 Bearer 토큰을 검증하여 현재 로그인한 사용자 정보를 반환합니다.
    이 함수는 각 엔드포인트에서 '의존성 주입' 방식으로 사용되어, 보호된 API를 만듭니다.
    """
    try:
        user_response = supabase.auth.get_user(token.credentials)
        user = user_response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )