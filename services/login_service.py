import os
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client as AsyncClient
from models.login_model import UserCreate
from gotrue.errors import AuthApiError
from .performance_monitor import measure_performance
import logging

logger = logging.getLogger(__name__)

@measure_performance("회원가입")
async def register_user(user: UserCreate, supabase: AsyncClient):
    """사용자 회원가입 및 user_account 테이블에 프로필 생성"""
    try:
        res = await supabase.auth.sign_up({
            "email": user.email, "password": user.password,
            "options": {"data": {"name": user.name}}
        })

        if res.user:
            account_data = {"user_id": str(res.user.id), "email": user.email, "name": user.name}
            await supabase.table("user_account").insert(account_data).execute()

            # 👇 [수정] res.session 유무에 따라 다른 메시지와 플래그를 반환합니다.
            if res.session:
                # 이메일 인증이 꺼져있어 바로 로그인 가능한 경우
                return {
                    "message": "회원가입이 성공적으로 완료되었습니다.",
                    "confirmation_required": False
                }
            else:
                # 이메일 인증이 필요하여 확인 메일이 발송된 경우
                return {
                    "message": "가입 확인 이메일이 발송되었습니다. 메일함을 확인해주세요.",
                    "confirmation_required": True
                }

        raise HTTPException(status_code=400, detail="회원가입 중 알 수 없는 오류가 발생했습니다.")

    except AuthApiError as e:
        if "User already registered" in str(e):
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        raise HTTPException(status_code=400, detail=f"회원가입 인증 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@measure_performance("프로필 생성")
async def create_user_profile(token: str, supabase: AsyncClient):
    """토큰으로 인증된 사용자의 프로필을 user_account 테이블에 생성합니다."""
    try:
        # 1. 토큰으로 사용자 정보 가져오기
        user_response = await supabase.auth.get_user(token)
        user = user_response.user
        if not user or not user.email or not user.user_metadata:
            raise HTTPException(status_code=401, detail="유효하지 않은 사용자 토큰입니다.")

        # 2. 프로필 데이터 생성 및 삽입
        account_data = {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.user_metadata.get("name")
        }
        await supabase.table("user_account").insert(account_data).execute()
        return {"message": "프로필이 성공적으로 생성되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 생성 중 오류 발생: {str(e)}")


@measure_performance("로그인")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm, supabase: AsyncClient):
    """로그인 처리 및 assessed_level을 포함한 JWT 토큰 반환"""
    try:
        print(f"--- 로그인 시도: {form_data.username} ---")
        res = await supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })

        if res.session and res.user and res.user.email:
            print(f"--- Supabase 인증 성공: {res.user.email} ---")

            profile_response = await supabase.table("user_account").select("assessed_level, is_admin").eq("email", res.user.email).maybe_single().execute()

            # 👇 [핵심 수정] 프로필이 존재하지 않는 경우를 안전하게 처리합니다.
            assessed_level = None
            is_admin = False

            if profile_response and profile_response.data:
                assessed_level = profile_response.data.get("assessed_level")
                is_admin = profile_response.data.get("is_admin", False)
                print(f"--- user_account에서 조회된 is_admin: {is_admin} ---")
            else:
                print("--- 경고: 'user_account' 테이블에 해당 유저의 프로필이 없습니다. ---")

            return {
                "access_token": res.session.access_token,
                "token_type": "bearer",
                "assessed_level": assessed_level,
                "is_admin": is_admin
            }

        raise HTTPException(status_code=401, detail="세션 또는 유저 정보가 없습니다.")

    except AuthApiError as e:
        print(f"### Supabase 인증 오류 발생: {e} ###")
        raise HTTPException(status_code=401, detail=f"인증 실패: {e.message}")
    except Exception as e:
        print(f"### 로그인 중 알 수 없는 오류 발생: {e} ###")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@measure_performance("프로필 조회")
async def get_current_user(token: str, supabase: AsyncClient):
    """JWT 토큰으로 사용자를 인증하고, DB 함수를 호출하여 전체 프로필을 조회합니다."""
    try:
        user_response = await supabase.auth.get_user(token)
        user = user_response.user
        if not user or not user.email:
            raise HTTPException(status_code=401, detail="인증 실패: 유효하지 않은 토큰입니다.")

        profile_response = await supabase.rpc('get_user_profile_by_email', {'user_email': user.email}).execute()

        if profile_response.data and len(profile_response.data) > 0:
            return profile_response.data[0]
        raise HTTPException(status_code=404, detail=f"프로필을 찾을 수 없습니다: {user.email}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 조회 중 서버 오류 발생: {str(e)}")

@measure_performance("평가 레벨 업데이트")
async def update_user_assessed_level(email: str, level: str, supabase: AsyncClient):
    """사용자의 평가 레벨을 이메일 기준으로 업데이트합니다."""
    try:
        # 👇 [디버깅 로그 추가] 레벨 업데이트가 어떤 값으로 시도되는지 확인합니다.
        print(f"--- 레벨 업데이트 시도: email={email}, level={level} ---")
        await supabase.table("user_account").update({"assessed_level": level}).eq("email", email).execute()
        print("--- 레벨 업데이트 성공 ---")
        return {"message": "사용자 레벨이 성공적으로 업데이트되었습니다."}
    except Exception as e:
        print(f"### 레벨 업데이트 중 오류 발생: {e} ###")
        raise HTTPException(status_code=500, detail=f"사용자 레벨 업데이트 중 오류 발생: {str(e)}")

@measure_performance("프로필 인증")
async def auto_login_with_token(token: str, supabase: AsyncClient):
    """JWT 토큰으로 사용자를 인증하고, 성공 시 'ok' 상태와 프로필을 반환합니다."""
    try:
        user_response = await supabase.auth.get_user(token)
        user = user_response.user
        if not user or not user.email:
            raise Exception("유효하지 않은 토큰입니다.")

        # get_user_profile_by_email 함수가 is_admin을 포함하도록 수정되었으므로
        # 이 부분은 자동으로 is_admin이 포함됩니다.
        profile_response = await supabase.rpc('get_user_profile_by_email', {'user_email': user.email}).execute()

        if profile_response.data and len(profile_response.data) > 0:
            profile_data = profile_response.data[0]
            print(f"--- 자동 로그인 프로필 데이터: {profile_data} ---")
            return {"status": "ok", "user_profile": profile_data}
        else:
            raise Exception("프로필을 찾을 수 없습니다.")
    except Exception as e:
        logger.warning(f"자동 로그인 실패: {e}")
        return {"status": "error", "message": str(e)}
