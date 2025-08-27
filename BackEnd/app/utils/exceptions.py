from fastapi import HTTPException
from fastapi.responses import JSONResponse

# ❌ 에러 응답
def http_error(status_code: int, message: str):
    """
    통일된 에러 응답 포맷
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": message,
            "code": status_code
        }
    )

# ✅ 성공 응답
def success_response(message: str, data: dict = None):
    """
    통일된 성공 응답 포맷
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )