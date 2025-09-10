import os
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client as AsyncClient
from models.login_model import UserCreate, UserUpdate

# 사용자 생성
async def register_user(user: UserCreate, supabase: AsyncClient):
    # 사용자 등록 요청
    try:
        res = await supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "is_admin": user.is_admin or False,
                }
            }
        })

        if res.user:
            return {"message": f"회원가입 성공. {user.email} 계정으로 확인 이메일이 발송되었을 수 있습니다."}
        else:
            raise HTTPException(status_code=400, detail="회원가입 중 오류가 발생했습니다.")

    except Exception as e:
        error_message = str(e)
        if "User already registered" in error_message:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        raise HTTPException(status_code=500, detail=f"서버 오류: {error_message}")

# 로그인 처리 및 JWT 토큰 반환
async def login_for_access_token(form_data: OAuth2PasswordRequestForm, supabase: AsyncClient):
    try:
        # Supabase에 이메일/비밀번호로 로그인 요청
        res = await supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })

        if res.session and res.session.access_token:
            return {"access_token": res.session.access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="로그인 정보가 유효하지 않습니다.")

    except Exception:
        raise HTTPException(status_code=401, detail="잘못된 이메일 또는 비밀번호입니다.")

# 로그인 페이지 URL 생성 및 반환
async def get_social_login_url(provider: str, supabase: AsyncClient):
    try:
        # 프론트엔드에서 소셜 로그인 후 돌아올 URL을 지정합니다.
        redirect_to = os.environ.get("FRONTEND_REDIRECT_URL", "http://localhost:8080")

        data = await supabase.auth.sign_in_with_oauth({
            "provider": provider,
            "options": {
                "redirect_to": redirect_to
            }
        })
        return {"url": data.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"소셜 로그인 URL 생성 실패: {e}")

# JWT 토큰을 사용하여 사용자 정보를 획득
async def get_current_user(token: str, supabase: AsyncClient):
    try:
        user_response = await supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            raise HTTPException(status_code=401, detail="인증 실패: 사용자를 찾을 수 없습니다.")

        return {"message": f"{user.email}님, 인증 성공!", "user_id": user.id, "user_metadata": user.user_metadata}

    except Exception:
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않거나 만료되었습니다.")


# 사용자의 정보(이메일, 비밀번호, is_admin) 수정
async def update_user_info(user_update: UserUpdate, token: str, supabase: AsyncClient):
    update_data = {}
    if user_update.email:
        update_data["email"] = user_update.email
    if user_update.password:
        update_data["password"] = user_update.password
    if user_update.is_admin is not None:
        update_data["data"] = {"is_admin": user_update.is_admin}

    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")

    try:
        # Supabase에 사용자 정보 업데이트 요청
        await supabase.auth.get_user(token)
        res = await supabase.auth.update_user(update_data)


        if res.user:
            return {"message": "사용자 정보가 성공적으로 수정되었습니다.", "updated_user": res.user.model_dump()}
        else:
            raise HTTPException(status_code=400, detail="사용자 정보 수정에 실패했습니다.")

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"수정 권한이 없거나 오류가 발생했습니다: {e}")
