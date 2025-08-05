from fastapi import HTTPException

def http_error(status_code: int, message: str):
    return HTTPException(
        status_code=status_code,
        detail={
            "error": message,
            "code": status_code
        }
    )