from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTPException 처리 핸들러
    모든 HTTP 예외를 {"error": {"code": int, "message": str}} 형식으로 반환
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail)
            }
        },
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    RequestValidationError 처리 핸들러
    필드명과 에러 메시지를 깔끔하게 가공하여 반환
    """
    error_messages = [
        f"{err['loc'][-1]}: {err['msg']}"
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": error_messages
            }
        },
    )