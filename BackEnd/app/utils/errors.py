from fastapi.responses import JSONResponse

def http_error(status_code: int, error_code: str, message: str):
    """
    API 에러 응답 형식을 통일하는 함수
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": message
        }
    )

def http_success(data=None, message: str = None):
    """
    API 성공 응답 형식을 통일하는 함수
    """
    response = {
        "success": True
    }
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return JSONResponse(status_code=200, content=response)